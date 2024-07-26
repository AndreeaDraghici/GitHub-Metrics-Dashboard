import requests
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .decorators import require_github_username
from .models import GitHubProfile

# Create your views here.

# Endpoint-uri GitHub API
GITHUB_API_URL = "https://api.github.com"
PERSONAL_ACCESS_TOKEN = "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"


def github_login(request) :
    return render(request, 'login.html')


@login_required
def register(request) :
    if request.method == 'POST' :
        github_username = request.POST['github_username']
        if github_username :
            profile, created = GitHubProfile.objects.get_or_create(user=request.user)
            profile.github_username = github_username
            profile.save()
            return redirect('profile')  # Redirect to the home page or any other page
        else :
            return render(request, 'register.html', {'error_message' : 'GitHub username is required.'})

    return render(request, 'register.html')


def github_callback(request) :
    user_info = requests.get(
        f"{GITHUB_API_URL}/user",
        headers={'Authorization' : f'token {PERSONAL_ACCESS_TOKEN}'}
    ).json()

    user, created = User.objects.get_or_create(username=user_info['login'])
    if created :
        github_profile = GitHubProfile(
            user=user,
            github_username=user_info['login'],
            avatar_url=user_info['avatar_url'],
            bio=user_info.get('bio', ''),
            location=user_info.get('location', '')
        )
        github_profile.save()

    # Log the user in
    login(request, user)

    return redirect('profile')


@login_required
@require_github_username
def profile(request) :
    github_profile = request.user.githubprofile
    repositories = requests.get(
        f"{GITHUB_API_URL}/user/repos",
        headers={'Authorization' : f'token {PERSONAL_ACCESS_TOKEN}'}
    ).json()
    context = {
        'profile' : github_profile,
        'repositories' : repositories
    }
    return render(request, 'profile.html', context)


@login_required
@require_github_username
def repo_detail(request, repo_name) :
    github_profile = request.user.githubprofile
    repo = requests.get(
        f"{GITHUB_API_URL}/repos/{github_profile.github_username}/{repo_name}",
        headers={'Authorization' : f'token {PERSONAL_ACCESS_TOKEN}'}
    ).json()
    context = {
        'repo' : repo
    }
    return render(request, 'repo_detail.html', context)


@login_required
@require_github_username
def get_activity_stats(request) :
    github_profile = request.user.githubprofile
    repos = requests.get(
        f"{GITHUB_API_URL}/user/repos",
        headers={'Authorization' : f'token {PERSONAL_ACCESS_TOKEN}'}
    ).json()

    commit_counts = []
    languages = {}

    for repo in repos :
        repo_name = repo['name']
        commits = requests.get(
            f"{GITHUB_API_URL}/repos/{github_profile.github_username}/{repo_name}/commits",
            headers={'Authorization' : f'token {PERSONAL_ACCESS_TOKEN}'}
        ).json()
        commit_counts.append({'repo' : repo_name, 'commits' : len(commits)})

        lang = repo['language']
        if lang :
            languages[lang] = languages.get(lang, 0) + 1

    languages = [{'language' : lang, 'count' : count} for lang, count in languages.items()]

    return JsonResponse({'commit_counts' : commit_counts, 'languages' : languages})


@login_required
@require_github_username
def activity_stats_page(request) :
    github_username = request.user.githubprofile.github_username
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
