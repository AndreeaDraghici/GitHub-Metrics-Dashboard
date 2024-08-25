from collections import defaultdict
from datetime import datetime

import requests
from django.conf import settings


# GitHub API service class
class APIService :
    ENDPOINT_URL = "https://api.github.com"

    @staticmethod
    def get_headers() :
        """
        Returns the headers required for making GitHub API requests,
        including the authorization token.
        """
        return {
            'Authorization' : f'token {settings.GITHUB_PERSONAL_ACCESS_TOKEN}',
            'Accept' : 'application/vnd.github.v3+json'
        }

    @classmethod
    def get_user_repositories(cls, github_username, page=1, per_page=100) :
        """
        Fetches repositories for a given GitHub user with pagination.

        :param github_username: GitHub username
        :param page: Page number to fetch
        :param per_page: Number of results per page (max 100)
        :return: List of repositories in JSON format
        """
        url = f"{cls.ENDPOINT_URL}/users/{github_username}/repos"
        params = {
            'per_page' : per_page,
            'page' : page
        }
        response = requests.get(url, headers=cls.get_headers(), params=params)

        if response.status_code != 200 :
            raise Exception(f"Error fetching user repos: {response.status_code} - {response.text}")

        return response.json()

    @classmethod
    def get_user_repository(cls, github_username, repo_name) :
        """
        Fetches repositories for a GitHub user and filters by repo_name.

        :param github_username: GitHub username
        :param repo_name: Repository name to filter
        :return: Repository information if found, otherwise None
        """
        page = 1
        while True :
            repos = cls.get_user_repositories(github_username, page=page)
            if not repos :
                break
            for repo in repos :
                if repo['name'].lower() == repo_name.lower() :
                    return repo
            page += 1
        return None

    @classmethod
    def get_repository_commits(cls, github_username, repo_name, page=1, per_page=100) :
        """
        Fetches all commits for a given repository of a GitHub user with pagination.

        :param github_username: GitHub username
        :param repo_name: Repository name
        :param page: Page number to fetch
        :param per_page: Number of results per page (max 100)
        :return: List of commits in JSON format
        """
        url = f"{cls.ENDPOINT_URL}/repos/{github_username}/{repo_name}/commits"
        params = {
            'per_page' : per_page,
            'page' : page
        }
        response = requests.get(url, headers=cls.get_headers(), params=params)

        if response.status_code != 200 :
            raise Exception(f"Error fetching repo commits: {response.status_code} - {response.text}")

        return response.json()

    @classmethod
    def get_repository_pull_requests(cls, github_username, repo_name, page=1, per_page=100) :
        """
        Fetches all pull requests for a given repository of a GitHub user with pagination.

        :param github_username: GitHub username
        :param repo_name: Repository name
        :param page: Page number to fetch
        :param per_page: Number of results per page (max 100)
        :return: List of pull requests in JSON format
        """
        url = f"{cls.ENDPOINT_URL}/repos/{github_username}/{repo_name}/pulls"
        params = {
            'state' : 'all',
            'per_page' : per_page,
            'page' : page
        }
        response = requests.get(url, headers=cls.get_headers(), params=params)

        if response.status_code != 200 :
            raise Exception(f"Error fetching repo pull requests: {response.status_code} - {response.text}")

        return response.json()

    @classmethod
    def get_repository_issues(cls, github_username, repo_name, page=1, per_page=100) :
        """
        Fetches all issues for a given repository of a GitHub user with pagination.

        :param github_username: GitHub username
        :param repo_name: Repository name
        :param page: Page number to fetch
        :param per_page: Number of results per page (max 100)
        :return: List of issues in JSON format
        """
        url = f"{cls.ENDPOINT_URL}/repos/{github_username}/{repo_name}/issues"
        params = {
            'state' : 'all',
            'per_page' : per_page,
            'page' : page
        }
        response = requests.get(url, headers=cls.get_headers(), params=params)

        if response.status_code != 200 :
            raise Exception(f"Error fetching repo issues: {response.status_code} - {response.text}")

        return response.json()

    @classmethod
    def get_repository_languages(cls, repo_languages_url) :
        """
        Fetches the programming languages used in a given repository.

        :param repo_languages_url: URL endpoint for repository languages
        :return: Dictionary of languages and their bytes in JSON format
        """
        response = requests.get(repo_languages_url, headers=cls.get_headers())

        if response.status_code != 200 :
            raise Exception(f"Error fetching repo languages: {response.status_code} - {response.text}")

        return response.json()

    @classmethod
    def create_repository(cls, name, description="", private=False) :
        """
        Creates a new repository for the authenticated user.

        :param name: Name of the repository
        :param description: Description of the repository
        :param private: Boolean indicating if the repository should be private
        :return: Response message indicating success or failure
        """
        url = f"{cls.ENDPOINT_URL}/user/repos"
        data = {
            'name' : name,
            'description' : description,
            'private' : private,
        }
        response = requests.post(url, json=data, headers=cls.get_headers())

        if response.status_code == 201 :
            return 'Repository created successfully.'
        else :
            return f'Error: {response.status_code} - {response.text}'

    @classmethod
    def delete_repository(cls, repo_name, github_username) :
        """
        Deletes a repository for the authenticated user.

        :param repo_name: Name of the repository to delete
        :param github_username: GitHub username
        :return: Response message indicating success or failure
        """
        url = f"{cls.ENDPOINT_URL}/repos/{github_username}/{repo_name}"
        response = requests.delete(url, headers=cls.get_headers())

        if response.status_code == 204 :
            return 'Repository deleted successfully.'
        else :
            return f'Error: {response.status_code} - {response.text}'

    @classmethod
    def get_user_information(cls, github_username) :
        """
        Fetches information for a given GitHub user.

        :param github_username: GitHub username
        :return: User information in JSON format
        """
        url = f"{cls.ENDPOINT_URL}/users/{github_username}"
        response = requests.get(url, headers=cls.get_headers())

        if response.status_code != 200 :
            raise Exception(f"Error fetching user info: {response.status_code} - {response.text}")

        return response.json()

    @classmethod
    def get_committer_date_activity(cls, repo_name, github_username) :
        params = {
            "per_page" : 100,
            "page" : 1
        }
        commits_url = f"{cls.ENDPOINT_URL}/repos/{github_username}/{repo_name}/commits"
        languages_activity = defaultdict(lambda : defaultdict(int))

        while True :
            response = requests.get(commits_url, headers=cls.get_headers(), params=params)
            commits = response.json()

            if not commits :
                break

            for commit in commits :
                commit_date = commit['commit']['committer']['date']
                commit_year_month = datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m")

                # Fetch the language stats for the commit's date
                languages_url = f"{cls.ENDPOINT_URL}/repos/{github_username}/{repo_name}/languages"
                languages_response = requests.get(languages_url, headers=cls.get_headers())
                languages = languages_response.json()

                for language, lines in languages.items() :
                    # lines = int(lines)
                    languages_activity[language][commit_year_month] += lines

            # Move to the next page
            params["page"] += 1

        return languages_activity
