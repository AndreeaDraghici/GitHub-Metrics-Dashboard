# github_app/middleware.py

from django.shortcuts import redirect

class CleanNextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        next_param = request.GET.get('next')
        if next_param:
            if len(next_param) > 200:
                # Prevent long URLs
                return redirect('/')
        response = self.get_response(request)
        return response
