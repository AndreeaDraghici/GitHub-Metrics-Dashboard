# github_app/middleware.py

from django.shortcuts import redirect
from django.shortcuts import render
from .services.github_api import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    GitHubAPIException
)


class CleanNextMiddleware :
    def __init__(self, get_response) :
        self.get_response = get_response

    def __call__(self, request) :
        next_param = request.GET.get('next')
        if next_param :
            if len(next_param) > 200 :
                # Prevent long URLs
                return redirect('/')
        response = self.get_response(request)
        return response


class GitHubAPIExceptionMiddleware :
    """
    Middleware to handle custom GitHub API exceptions globally.
    """

    def __init__(self, get_response) :
        self.get_response = get_response

    def __call__(self, request) :
        try :
            response = self.get_response(request)
            return response
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
