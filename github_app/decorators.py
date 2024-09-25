# decorators.py

from django.http import HttpResponseForbidden

from django.shortcuts import render
from .services.github_api import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    GitHubAPIException
)


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


def handle_github_exceptions(view_func) :
    """
    Decorator to handle custom GitHub API exceptions and render appropriate error pages.
    """

    def wrapper(request, *args, **kwargs) :
        try :
            return view_func(request, *args, **kwargs)
        except AuthenticationError as e :
            return render(request, 'errors/api_error.html', {'error_message' : str(e)}, status=401)
        except NotFoundError as e :
            return render(request, 'errors/404.html', {'error_message' : str(e)}, status=404)
        except RateLimitError as e :
            return render(request, 'errors/api_error.html', {'error_message' : str(e)}, status=429)
        except ServerError as e :
            return render(request, 'errors/500.html', {'error_message' : str(e)}, status=500)
        except GitHubAPIException as e :
            return render(request, 'errors/api_error.html', {'error_message' : str(e)}, status=400)
        except Exception as e :
            # Optionally log the exception here
            return render(request, 'errors/api_error.html', {'error_message' : 'An unexpected error occurred.'},
                          status=500)

    return wrapper
