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
        return {'Authorization' : f'token {settings.GITHUB_PERSONAL_ACCESS_TOKEN}'}

    @classmethod
    def get_user_info(cls, github_username) :
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
    def get_user_repos(cls, github_username) :
        """
        Fetches all repositories for a given GitHub user.

        :param github_username: GitHub username
        :return: List of repositories in JSON format
        """
        url = f"{cls.ENDPOINT_URL}/users/{github_username}/repos"
        response = requests.get(url, headers=cls.get_headers())

        if response.status_code != 200 :
            raise Exception(f"Error fetching user repos: {response.status_code} - {response.text}")

        return response.json()

    @classmethod
    def get_user_repo(cls, github_username, repo_name) :
        """
        Fetches repositories for a GitHub user and filters by repo_name.

        :param github_username: GitHub username
        :param repo_name: Repository name to filter
        :return: Repository information if found, otherwise None
        """
        url = f'{cls.ENDPOINT_URL}/users/{github_username}/repos'
        response = requests.get(url, headers=cls.get_headers())

        if response.status_code != 200 :
            raise Exception(f"Error fetching repos: {response.status_code} - {response.text}")

        repos = response.json()
        # Find the repository with the matching name
        for repo in repos :
            if repo['name'].lower() == repo_name.lower() :
                return repo
        return None

    @classmethod
    def get_repo_commits(cls, github_username, repo_name) :
        """
        Fetches all commits for a given repository of a GitHub user.

        :param github_username: GitHub username
        :param repo_name: Repository name
        :return: List of commits in JSON format
        """
        url = f"{cls.ENDPOINT_URL}/repos/{github_username}/{repo_name}/commits"
        response = requests.get(url, headers=cls.get_headers())

        if response.status_code != 200 :
            raise Exception(f"Error fetching repo commits: {response.status_code} - {response.text}")

        return response.json()

    @classmethod
    def get_repo_prs(cls, github_username, repo_name) :
        """
        Fetches all pull requests for a given repository of a GitHub user.

        :param github_username: GitHub username
        :param repo_name: Repository name
        :return: List of pull requests in JSON format
        """
        url = f"{cls.ENDPOINT_URL}/repos/{github_username}/{repo_name}/pulls?state=all"
        response = requests.get(url, headers=cls.get_headers())

        if response.status_code != 200 :
            raise Exception(f"Error fetching repo pull requests: {response.status_code} - {response.text}")

        return response.json()

    @classmethod
    def get_repo_issues(cls, github_username, repo_name) :
        """
        Fetches all issues for a given repository of a GitHub user.

        :param github_username: GitHub username
        :param repo_name: Repository name
        :return: List of issues in JSON format
        """
        url = f"{cls.ENDPOINT_URL}/repos/{github_username}/{repo_name}/issues?state=all"
        response = requests.get(url, headers=cls.get_headers())

        if response.status_code != 200 :
            raise Exception(f"Error fetching repo issues: {response.status_code} - {response.text}")

        return response.json()

    @classmethod
    def get_repo_languages(cls, repo_languages_url) :
        """
        Fetches the programming languages used in a given repository.

        :param repo_languages_url: URL endpoint for repository languages
        :return: Dictionary of languages and their bytes in JSON format
        """
        response = requests.get(repo_languages_url, headers=cls.get_headers())

        if response.status_code != 200 :
            raise Exception(f"Error fetching repo languages: {response.status_code} - {response.text}")

        return response.json()
