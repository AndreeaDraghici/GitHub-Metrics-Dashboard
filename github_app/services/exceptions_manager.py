
# Custom Exceptions
class GitHubAPIException(Exception) :
    """Base exception for GitHub API errors."""
    pass


class AuthenticationError(GitHubAPIException) :
    """Exception raised for authentication failures."""
    pass


class NotFoundError(GitHubAPIException) :
    """Exception raised when a resource is not found."""
    pass


class RateLimitError(GitHubAPIException) :
    """Exception raised when rate limit is exceeded."""
    pass


class ServerError(GitHubAPIException) :
    """Exception raised for server-side errors."""
    pass
