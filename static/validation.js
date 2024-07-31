document.addEventListener('DOMContentLoaded', function() {
    const usernameInput = document.getElementById('github_username');
    const errorMessage = document.getElementById('username-error');

    usernameInput.addEventListener('input', function() {
        const username = usernameInput.value.trim();
        if (username === '') {
            errorMessage.textContent = '';
            return;
        }

        // Check if the username is already being checked
        if (usernameInput.dataset.checking === 'true') {
            return;
        }

        // Indicate that a check is in progress
        usernameInput.dataset.checking = 'true';

        fetch(`https://api.github.com/users/${username}`)
            .then(response => {
                if (response.ok) {
                    errorMessage.textContent = ''; // Clear error message
                } else {
                    errorMessage.textContent = 'GitHub username does not exist.';
                }
                usernameInput.dataset.checking = 'false'; // Allow further checks
            })
            .catch(() => {
                errorMessage.textContent = 'Error checking GitHub username.';
                usernameInput.dataset.checking = 'false'; // Allow further checks
            });
    });
});