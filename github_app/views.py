import requests
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

from .decorators import require_github_username

# Endpoint-uri GitHub API
GITHUB_API_URL = "https://api.github.com"
PERSONAL_ACCESS_TOKEN = "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"


def github_login(request) :
    # Clear session data on login page to ensure a fresh start
    request.session.flush()
    return render(request, 'login.html')


# @login_required
def register(request) :
    if request.method == 'POST' :
        github_username = request.POST.get('github_username')
        if github_username :
            # Temporarily store the GitHub username in the session
            request.session['github_username'] = github_username
            return redirect('github_callback')  # Redirect to GitHub callback to fetch user data
        else :
            return render(request, 'register.html', {'error_message' : 'GitHub username is required.'})

    return render(request, 'register.html')


# @login_required
def github_callback(request) :
    github_username = request.session.get('github_username')
    if not github_username :
        return redirect('register')  # Redirect to registration if GitHub username is not in the session

    # Fetch user info using the GitHub API
    user_info = requests.get(
        f"{GITHUB_API_URL}/users/{github_username}",
        headers={'Authorization' : f'token {PERSONAL_ACCESS_TOKEN}'}
    ).json()

    # Create a user object and log the user in
    user, _ = User.objects.get_or_create(username=user_info['login'])
    login(request, user)

    return redirect('profile')


# @login_required
def profile(request) :
    github_username = request.session.get('github_username')
    if not github_username :
        return redirect('register')  # Redirect to registration if GitHub username is not in the session

    user_info = requests.get(
        f"{GITHUB_API_URL}/users/{github_username}",
        headers={'Authorization' : f'token {PERSONAL_ACCESS_TOKEN}'}
    ).json()

    repositories = requests.get(
        f"{GITHUB_API_URL}/users/{github_username}/repos",
        headers={'Authorization' : f'token {PERSONAL_ACCESS_TOKEN}'}
    ).json()

    context = {
        'profile' : user_info,
        'repositories' : repositories
    }
    return render(request, 'profile.html', context)


# @login_required
# @require_github_username
def repo_detail(request, repo_name) :
    github_username = request.session.get('github_username')
    if not github_username :
        return redirect('register')  # Redirect to registration if GitHub username is not in the session

    repo = requests.get(
        f"{GITHUB_API_URL}/repos/{github_username}/{repo_name}",
        headers={'Authorization' : f'token {PERSONAL_ACCESS_TOKEN}'}
    ).json()
    context = {
        'repo' : repo
    }
    return render(request, 'repo_detail.html', context)


# @login_required
# @require_github_username
def contribution_stats(request) :
    github_username = request.session.get('github_username')
    if not github_username :
        return redirect('register')  # Redirect to registration if GitHub username is not in the session

    user_data = requests.get(
        f"{GITHUB_API_URL}/users/{github_username}",
        headers={'Authorization' : f'token {PERSONAL_ACCESS_TOKEN}'}
    ).json()

    repos = requests.get(
        f"{GITHUB_API_URL}/users/{github_username}/repos",
        headers={'Authorization' : f'token {PERSONAL_ACCESS_TOKEN}'}
    ).json()

    repository_details = []
    total_commits = 0
    for repo in repos :
        repo_name = repo['name']
        commits = requests.get(
            f"{GITHUB_API_URL}/repos/{github_username}/{repo_name}/commits",
            headers={'Authorization' : f'token {PERSONAL_ACCESS_TOKEN}'}
        ).json()
        commit_count = len(commits)
        total_commits += commit_count
        repository_details.append({
            'name' : repo.get('name', 'N/A'),
            'description' : repo.get('description', 'No description'),
            'language' : repo.get('language', 'Unknown'),
            'created_at' : repo.get('created_at', 'N/A'),
            'updated_at' : repo.get('updated_at', 'N/A'),
            'html_url' : repo.get('html_url', '#')
        })

    total_repos = len(repos)
    account_created_at = user_data.get('created_at', 'N/A')
    last_updated_at = user_data.get('updated_at', 'N/A')

    # Count the number of repositories for each language
    languages = {}
    for repo in repos :
        lang = repo['language']
        if lang :
            languages[lang] = languages.get(lang, 0) + 1
    sorted_languages = sorted(languages.items(), key=lambda x : x[1], reverse=True)

    context = {
        'github_username' : github_username,
        'repository_details' : repository_details,
        'total_commits' : total_commits,
        'total_repos' : total_repos,
        'account_created_at' : account_created_at,
        'last_updated_at' : last_updated_at,
        'sorted_languages' : sorted_languages
    }

    return render(request, 'contribution_stats.html', context)


# @login_required
# @require_github_username
def activity_stats_page(request) :
    github_username = request.session.get('github_username')
    if not github_username :
        return redirect('register')  # Redirect to registration if GitHub username is not in the session

    headers = {'Authorization' : f'token {PERSONAL_ACCESS_TOKEN}'}

    # Fetch repositories
    repos_response = requests.get(f'https://api.github.com/users/{github_username}/repos', headers=headers)
    repos_data = repos_response.json()

    # Metrics initialization
    total_commits = 0
    total_stars = 0
    total_forks = 0
    pull_requests = []
    issues = []

    for repo in repos_data :
        repo_name = repo['name']
        total_stars += repo['stargazers_count']
        total_forks += repo['forks_count']

        # Fetch commits count
        commits_response = requests.get(f'https://api.github.com/repos/{github_username}/{repo_name}/commits',
                                        headers=headers)
        commits_data = commits_response.json()
        commits_count = len(commits_data)
        total_commits += commits_count
        repo['commits_count'] = commits_count

        # Fetch pull requests count
        prs_response = requests.get(f'https://api.github.com/repos/{github_username}/{repo_name}/pulls?state=all',
                                    headers=headers)
        prs_data = prs_response.json()
        prs_count = len(prs_data)
        pull_requests.extend(prs_data)
        repo['prs_count'] = prs_count

        # Fetch issues count
        issues_response = requests.get(f'https://api.github.com/repos/{github_username}/{repo_name}/issues?state=all',
                                       headers=headers)
        issues_data = issues_response.json()
        issues_count = len(issues_data)
        issues.extend(issues_data)
        repo['issues_count'] = issues_count

    # Process pull requests
    total_prs = len(pull_requests)
    merged_prs = sum(1 for pr in pull_requests if pr['merged_at'])

    # Process issues
    total_issues = len(issues)
    closed_issues = sum(1 for issue in issues if issue['state'] == 'closed')

    stats = {
        'repo_count' : len(repos_data),
        'total_commits' : total_commits,
        'total_stars' : total_stars,
        'total_forks' : total_forks,
        'total_prs' : total_prs,
        'merged_prs' : merged_prs,
        'total_issues' : total_issues,
        'closed_issues' : closed_issues,
        'repos' : repos_data
    }

    # Render the template with the stats
    return render(request, 'activity_stats_page.html', stats)


def language_statistics(request) :
    github_username = request.session.get('github_username')
    if not github_username :
        return redirect('register')

    # Obține lista de repozitorii
    repositories = requests.get(
        f"{GITHUB_API_URL}/users/{github_username}/repos",
        headers={'Authorization' : f'token {PERSONAL_ACCESS_TOKEN}'}
    ).json()

    language_data = {}
    total_bytes = 0
    for repo in repositories :
        languages = requests.get(
            repo['languages_url'],
            headers={'Authorization' : f'token {PERSONAL_ACCESS_TOKEN}'}
        ).json()
        for language, bytes in languages.items() :
            if language in language_data :
                language_data[language] += bytes
            else :
                language_data[language] = bytes
            total_bytes += bytes

    language_percentages = {}
    for language, bytes in language_data.items() :
        percentage = (bytes / total_bytes) * 100
        language_percentages[language] = percentage

    sorted_language_percentages = sorted(language_percentages.items(), key=lambda item : item[1], reverse=True)

    context = {
        'language_percentages' : sorted_language_percentages
    }
    return render(request, 'language_statistics.html', context)
