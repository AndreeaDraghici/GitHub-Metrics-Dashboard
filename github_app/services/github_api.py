from collections import defaultdict
from datetime import datetime
import requests
from django.conf import settings

from github_app.services.exceptions_manager import AuthenticationError, RateLimitError, GitHubAPIException, \
    NotFoundError, ServerError


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
    def handle_response(cls, response, error_context="") :
        """
        Handles the HTTP response, raising appropriate exceptions for error statuses.

        :param response: The HTTP response object
        :param error_context: Additional context for the error message
        :return: JSON data if the response is successful
        """
        if response.status_code == 200 or response.status_code == 201 or response.status_code == 204 :
            if response.status_code == 204 :
                return None  # No Content
            return response.json()
        elif response.status_code == 401 :
            raise AuthenticationError(
                f"Authentication failed: {response.status_code} - {response.json().get('message', '')}")
        elif response.status_code == 403 :
            if 'rate limit' in response.text.lower() :
                raise RateLimitError(
                    f"Rate limit exceeded: {response.status_code} - {response.json().get('message', '')}")
            else :
                raise GitHubAPIException(f"Forbidden: {response.status_code} - {response.json().get('message', '')}")
        elif response.status_code == 404 :
            raise NotFoundError(f"Resource not found: {response.status_code} - {response.json().get('message', '')}")
        elif 400 <= response.status_code < 500 :
            raise GitHubAPIException(f"Client error: {response.status_code} - {response.json().get('message', '')}")
        elif 500 <= response.status_code < 600 :
            raise ServerError(f"Server error: {response.status_code} - {response.json().get('message', '')}")
        else :
            raise GitHubAPIException(f"Unexpected error ({response.status_code}): {response.text}")

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
        return cls.handle_response(response, "fetching user repositories")

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
        raise NotFoundError(f"Repository '{repo_name}' not found for user '{github_username}'.")

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
        return cls.handle_response(response, "fetching repository commits")

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
        return cls.handle_response(response, "fetching repository pull requests")

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
        return cls.handle_response(response, "fetching repository issues")

    @classmethod
    def get_repository_languages(cls, repo_languages_url) :
        """
        Fetches the programming languages used in a given repository.

        :param repo_languages_url: URL endpoint for repository languages
        :return: Dictionary of languages and their bytes in JSON format
        """
        response = requests.get(repo_languages_url, headers=cls.get_headers())
        return cls.handle_response(response, "fetching repository languages")

    @classmethod
    def create_repository(cls, name, description="", private=False) :
        """
        Creates a new repository for the authenticated user.

        :param name: Name of the repository
        :param description: Description of the repository
        :param private: Boolean indicating if the repository should be private
        :return: Success message
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
            cls.handle_response(response, "creating repository")

    @classmethod
    def delete_repository(cls, repo_name, github_username) :
        """
        Deletes a repository for the authenticated user.

        :param repo_name: Name of the repository to delete
        :param github_username: GitHub username
        :return: Success message
        """
        url = f"{cls.ENDPOINT_URL}/repos/{github_username}/{repo_name}"
        response = requests.delete(url, headers=cls.get_headers())
        if response.status_code == 204 :
            return 'Repository deleted successfully.'
        else :
            cls.handle_response(response, "deleting repository")

    @classmethod
    def get_user_information(cls, github_username) :
        """
        Fetches information for a given GitHub user.

        :param github_username: GitHub username
        :return: User information in JSON format
        """
        url = f"{cls.ENDPOINT_URL}/users/{github_username}"
        response = requests.get(url, headers=cls.get_headers())
        return cls.handle_response(response, "fetching user information")

    @classmethod
    def get_committer_date_activity(cls, repo_name, github_username) :
        """
        Analyzes the activity of different programming languages over time based on commit data.

        :param repo_name: Name of the repository
        :param github_username: GitHub username
        :return: Nested dictionary with language activity per month
        """
        params = {
            "per_page" : 100,
            "page" : 1
        }
        commits_url = f"{cls.ENDPOINT_URL}/repos/{github_username}/{repo_name}/commits"
        languages_activity = defaultdict(lambda : defaultdict(int))

        while True :
            response = requests.get(commits_url, headers=cls.get_headers(), params=params)
            try :
                commits = cls.handle_response(response, "fetching commits for activity analysis")
            except GitHubAPIException as e :
                # Depending on your use case, you might want to log this error
                raise GitHubAPIException(f"Failed to retrieve commits: {e}")

            if not commits :
                break

            for commit in commits :
                commit_date_str = commit['commit']['committer']['date']
                commit_date = datetime.strptime(commit_date_str, "%Y-%m-%dT%H:%M:%SZ")
                commit_year_month = commit_date.strftime("%Y-%m")

                # Fetch the language stats for the repository
                languages_url = f"{cls.ENDPOINT_URL}/repos/{github_username}/{repo_name}/languages"
                languages_response = requests.get(languages_url, headers=cls.get_headers())
                try :
                    languages = cls.handle_response(languages_response, "fetching languages for activity analysis")
                except GitHubAPIException as e :
                    raise GitHubAPIException(f"Failed to retrieve languages: {e}")

                for language, bytes_of_code in languages.items() :
                    languages_activity[language][commit_year_month] += bytes_of_code

            # Move to the next page
            params["page"] += 1

        return languages_activity
