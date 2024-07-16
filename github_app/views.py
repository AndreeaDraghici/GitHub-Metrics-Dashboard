import requests
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import GitHubProfile, Repository
from django.contrib.auth import login
import matplotlib.pyplot as plt
import io
import base64
# Create your views here.

# Endpoint-uri GitHub API
GITHUB_API_URL = "https://api.github.com"
PERSONAL_ACCESS_TOKEN = "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"


def github_login(request) :
    return render(request, 'login.html')  # Un template simplu pentru autentificare


def register(request) :
    if request.method == 'POST' :
        github_username = request.POST.get('github_username')

        # Trimite cerere către API-ul GitHub pentru a obține informațiile utilizatorului
        response = requests.get(
            f"{GITHUB_API_URL}/users/{github_username}",
            headers={'Accept' : 'application/vnd.github.v3+json'}
        )

        if response.status_code == 200 :
            user_info = response.json()

            # Verifică dacă utilizatorul există deja în baza de date
            user, created = User.objects.get_or_create(username=github_username)

            # Actualizează sau creează profilul GitHub asociat utilizatorului
            github_profile, created = GitHubProfile.objects.update_or_create(
                user=user,
                defaults={
                    'github_username' : github_username,
                    'avatar_url' : user_info.get('avatar_url', ''),
                    'bio' : user_info.get('bio', ''),
                    'location' : user_info.get('location', '')
                }
            )

            return redirect('profile')
        else :
            # Tratează cazul în care nu s-a găsit utilizatorul GitHub
            error_message = f"GitHub username '{github_username}' not found."
            context = {'error_message' : error_message}
            return render(request, 'register.html', context)

    return render(request, 'register.html')


def github_callback(request) :
    # Folosim token-ul direct, deci această funcție poate fi simplificată
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
def activity_stats(request) :
    github_profile = request.user.githubprofile
    repos = requests.get(
        f"{GITHUB_API_URL}/user/repos",
        headers={'Authorization' : f'token {PERSONAL_ACCESS_TOKEN}'}
    ).json()

    commit_counts = []
    languages = {}
    repo_names = []

    for repo in repos :
        repo_name = repo['name']
        repo_names.append(repo_name)

        commits = requests.get(
            f"{GITHUB_API_URL}/repos/{github_profile.github_username}/{repo_name}/commits",
            headers={'Authorization' : f'token {PERSONAL_ACCESS_TOKEN}'}
        ).json()
        commit_counts.append(len(commits))

        lang = repo['language']
        if lang :
            languages[lang] = languages.get(lang, 0) + 1

    # Sort languages by usage
    languages = dict(sorted(languages.items(), key=lambda item : item[1], reverse=True))
    lang_names = list(languages.keys())
    lang_counts = list(languages.values())

    context = {
        'profile' : github_profile,
        'repo_names' : repo_names,
        'commit_counts' : commit_counts,
        'lang_names' : lang_names,
        'lang_counts' : lang_counts
    }
    return render(request, 'activity_stats.html', context)