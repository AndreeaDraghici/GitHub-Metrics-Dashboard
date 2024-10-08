import concurrent.futures
import concurrent.futures
from collections import defaultdict

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from .decorators import handle_github_exceptions  # Import the decorator
from .services.github_api import APIService


# your_app_name/views.py


@handle_github_exceptions
def github_login(request) :
    # Clear session data on login page to ensure a fresh start
    request.session.flush()
    return render(request, 'login.html')


@handle_github_exceptions
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


@handle_github_exceptions
def github_callback(request) :
    github_username = request.session.get('github_username')
    if not github_username :
        return redirect('register')  # Redirect to registration if GitHub username is not in the session

    # Fetch user info using the GitHub API
    user_info = APIService.get_user_information(github_username)

    # Create a user object and log the user in
    user, _ = User.objects.get_or_create(username=user_info['login'])
    login(request, user)

    return redirect('profile')


@handle_github_exceptions
def profile(request) :
    github_username = request.session.get('github_username')
    if not github_username :
        return redirect('register')  # Redirect to registration if GitHub username is not in the session

    user_info = APIService.get_user_information(github_username)
    repositories = APIService.get_user_repositories(github_username)

    context = {
        'profile' : user_info,
        'repositories' : repositories
    }
    return render(request, 'profile.html', context)


@handle_github_exceptions
def repo_detail(request, repo_name) :
    github_username = request.session.get('github_username')
    if not github_username :
        return redirect('register')  # Redirect to registration if GitHub username is not in the session

    repo = APIService.get_user_repository(github_username, repo_name)
    context = {
        'repo' : repo
    }
    return render(request, 'repo_detail.html', context)


@handle_github_exceptions
def contribution_stats(request) :
    github_username = request.session.get('github_username')
    if not github_username :
        return redirect('register')  # Redirect to registration if GitHub username is not in the session

    user_data = APIService.get_user_information(github_username)
    repos = APIService.get_user_repositories(github_username)

    repository_details = []
    total_commits = 0
    for repo in repos :
        repo_name = repo['name']
        commits = APIService.get_repository_commits(github_username, repo_name)
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


@handle_github_exceptions
def activity_stats_page(request) :
    github_username = request.session.get('github_username')
    if not github_username :
        return redirect('register')  # Redirect to registration if GitHub username is not in the session

    repos_data = APIService.get_user_repositories(github_username)

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
        commits_data = APIService.get_repository_commits(github_username, repo_name)
        commits_count = len(commits_data)
        total_commits += commits_count
        repo['commits_count'] = commits_count

        # Fetch pull requests count
        prs_data = APIService.get_repository_pull_requests(github_username, repo_name)
        prs_count = len(prs_data)
        pull_requests.extend(prs_data)
        repo['prs_count'] = prs_count

        # Fetch issues count
        issues_data = APIService.get_repository_issues(github_username, repo_name)
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


@handle_github_exceptions
def language_statistics(request) :
    github_username = request.session.get('github_username')

    # Redirect if the user is not logged in
    if not github_username :
        return redirect('register')

    # Fetch repositories once and reuse for both percentage and activity calculations
    repositories = APIService.get_user_repositories(github_username)

    # Get language percentages and activity data using the repositories list
    sorted_language_percentages = get_language_percentages_from_repos(repositories)
    languages_activity = get_languages_activity_from_repos(repositories, github_username)

    # Prepare context for template
    context = {
        'language_percentages' : sorted_language_percentages,
        'languages_activity' : languages_activity
    }

    return render(request, 'language_statistics.html', context)


@handle_github_exceptions
def github_interactions(request) :
    github_username = request.session.get('github_username')
    if not github_username :
        return redirect('register')  # Redirect to registration if GitHub username is not in the session

    if request.method == 'POST' :
        action = request.POST.get('action')
        if action == 'create_repo' :
            return create_repo(request)
        elif action == 'delete_repo' :
            return delete_repo(request)

    # Fetch repositories to display in the deletion modal
    repositories = APIService.get_user_repositories(github_username)
    return render(request, 'github_interactions.html', {'repositories' : repositories})


@handle_github_exceptions
def create_repo(request) :
    github_username = request.session.get('github_username')
    if not github_username :
        return redirect('register')  # Redirect to registration if GitHub username is not in the session

    repo_name = request.POST.get('name')
    description = request.POST.get('description')
    private = request.POST.get('private') == 'true'

    # Pass only the parameters expected by the create_repository method
    message = APIService.create_repository(repo_name, description, private)

    # Fetch updated list of repositories after creation
    repositories = APIService.get_user_repositories(github_username)

    return render(request, 'github_interactions.html', {'modal_message' : message, 'repositories' : repositories})


@handle_github_exceptions
def delete_repo(request) :
    github_username = request.session.get('github_username')
    if not github_username :
        return redirect('register')  # Redirect to registration if GitHub username is not in the session

    repo_name = request.POST.get('repo_name')
    message = APIService.delete_repository(github_username, repo_name)
    # Fetch updated list of repositories
    repositories = APIService.get_user_repositories(github_username)
    return render(request, 'github_interactions.html', {'modal_message' : message, 'repositories' : repositories})


def get_language_percentages_from_repos(repositories) :
    language_data = defaultdict(int)
    total_bytes = 0

    def fetch_languages(repo) :
        return APIService.get_repository_languages(repo['languages_url'])

    with concurrent.futures.ThreadPoolExecutor() as executor :
        results = executor.map(fetch_languages, repositories)
        for languages in results :
            for language, bytes in languages.items() :
                language_data[language] += bytes
                total_bytes += bytes

    sorted_language_percentages = sorted(
        ((language, (bytes / total_bytes) * 100) for language, bytes in language_data.items()),
        key=lambda item : item[1],
        reverse=True
    )

    return sorted_language_percentages


def get_languages_activity_from_repos(repositories, github_username) :
    languages_activity = defaultdict(lambda : defaultdict(int))

    for repo in repositories :
        repo_languages_activity = APIService.get_committer_date_activity(repo['name'], github_username)
        for language, monthly_data in repo_languages_activity.items() :
            for date, lines in monthly_data.items() :
                # Ensure that `lines` is an integer
                try :
                    lines = int(lines)
                except ValueError :
                    lines = 0  # Handle or log the error as needed

                languages_activity[language][date] += lines

    return {language : dict(dates) for language, dates in languages_activity.items()}


def custom_404(request, exception) :
    return render(request, 'errors/404.html', status=404)


def custom_500(request) :
    return render(request, 'errors/500.html', status=500)
