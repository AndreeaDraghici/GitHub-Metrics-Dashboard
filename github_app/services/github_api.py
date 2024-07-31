import requests
from django.conf import settings


# GitHub API service class
class APIService :
    ENDPOINT_URL = "https://api.github.com"

    @staticmethod
    def get_headers() :
        return {'Authorization' : f'token {settings.GITHUB_PERSONAL_ACCESS_TOKEN}'}

    @classmethod
    def get_user_info(cls, github_username) :
        url = f"{cls.ENDPOINT_URL}/users/{github_username}"
        return requests.get(url, headers=cls.get_headers()).json()

    @classmethod
    def get_user_repos(cls, github_username) :
        url = f"{cls.ENDPOINT_URL}/users/{github_username}/repos"
        return requests.get(url, headers=cls.get_headers()).json()

    @classmethod
    def get_repo_commits(cls, github_username, repo_name) :
        url = f"{cls.ENDPOINT_URL}/repos/{github_username}/{repo_name}/commits"
        return requests.get(url, headers=cls.get_headers()).json()

    @classmethod
    def get_repo_prs(cls, github_username, repo_name) :
        url = f"{cls.ENDPOINT_URL}/repos/{github_username}/{repo_name}/pulls?state=all"
        return requests.get(url, headers=cls.get_headers()).json()

    @classmethod
    def get_repo_issues(cls, github_username, repo_name) :
        url = f"{cls.ENDPOINT_URL}/repos/{github_username}/{repo_name}/issues?state=all"
        return requests.get(url, headers=cls.get_headers()).json()

    @classmethod
    def get_repo_languages(cls, repo_languages_url) :
        return requests.get(repo_languages_url, headers=cls.get_headers()).json()
