from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class GitHubProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    github_username = models.CharField(max_length=255)
    avatar_url = models.URLField(max_length=200)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

class Repository(models.Model):
    github_profile = models.ForeignKey(GitHubProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    html_url = models.URLField(max_length=200)
    language = models.CharField(max_length=100, blank=True, null=True)
    stargazers_count = models.IntegerField(default=0)
    forks_count = models.IntegerField(default=0)