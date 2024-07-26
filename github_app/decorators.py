# decorators.py

from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseForbidden


def require_github_username(view_func) :
    def _wrapped_view_func(request, *args, **kwargs) :
        if request.user.is_authenticated :
            try :
                profile = request.user.githubprofile
                if not profile.github_username :
                    return HttpResponseForbidden("Access Denied: You need to register your GitHub username.")
            except request.user.DoesNotExist :
                return HttpResponseForbidden("Access Denied: You need to register your GitHub username.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view_func
