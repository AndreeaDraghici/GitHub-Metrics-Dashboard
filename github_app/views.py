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


@login_required
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


@login_required
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


@login_required
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


@login_required
@require_github_username
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


@login_required
@require_github_username
def contribution_stats(request) :
    github_username = request.session.get('github_username')
    if not github_username :
        return redirect('register')  # Redirect to registration if GitHub username is not in the session

    # Fetch repositories
    repos_response = requests.get(
        f"{GITHUB_API_URL}/users/{github_username}/repos",
        headers={'Authorization' : f'token {PERSONAL_ACCESS_TOKEN}'}
    )
    repos = repos_response.json()

    # Initialize counters and data structures
    total_commits = 0
    total_stars = 0
    total_forks = 0
    language_counts = {}
    repository_details = []

    for repo in repos :
        repo_name = repo['name']
        total_stars += repo['stargazers_count']
        total_forks += repo['forks_count']

        # Fetch commits for each repository
        commits_response = requests.get(
            f"{GITHUB_API_URL}/repos/{github_username}/{repo_name}/commits",
            headers={'Authorization' : f'token {PERSONAL_ACCESS_TOKEN}'}
        )
        commits = commits_response.json()
        total_commits += len(commits)

        # Count languages
        language = repo['language']
        if language :
            language_counts[language] = language_counts.get(language, 0) + 1

        # Collect repository details
        repository_details.append({
            'name' : repo_name,
            'stars' : repo['stargazers_count'],
            'forks' : repo['forks_count'],
            'commits' : len(commits),
            'language' : language
        })

    # Convert language counts to a sorted list of tuples
    sorted_languages = sorted(language_counts.items(), key=lambda item : item[1], reverse=True)

    # Prepare context data
    context = {
        'total_commits' : total_commits,
        'total_stars' : total_stars,
        'total_forks' : total_forks,
        'sorted_languages' : sorted_languages,
        'repository_details' : repository_details
    }

    return render(request, 'contribution_stats.html', context)

@login_required
@require_github_username
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
