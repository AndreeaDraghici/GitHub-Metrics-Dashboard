document.addEventListener('DOMContentLoaded', function() {
    const createRepoForm = document.getElementById('createRepoForm');
    const modal = document.getElementById('responseModal');
    const modalMessage = document.getElementById('modalMessage');
    const closeModal = document.querySelector('.modal .close');

    createRepoForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission

        // Collect form data
        const repoName = document.getElementById('repoName').value;
        const description = document.getElementById('description').value;
        const isPrivate = document.getElementById('private').checked;

        // Prepare data for POST request
        const data = {
            name: repoName,
            description: description,
            private: isPrivate,
        };

        fetch(createRepoForm.action, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
        .then(response => response.text())
        .then(text => {
            // Check if response contains success or error messages
            if (text.includes('Repository created successfully')) {
                modalMessage.textContent = 'Repository created successfully';
                modal.style.display = 'block';
            } else if (text.includes('Error:')) {
                modalMessage.textContent = text;
                modal.style.display = 'block';
            } else {
                modalMessage.textContent = 'Unexpected response';
                modal.style.display = 'block';
            }
        })
        .catch(error => {
            modalMessage.textContent = 'Error: ' + error.message;
            modal.style.display = 'block';
        });
    });

    // Close the modal when the user clicks on <span> (x)
    closeModal.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    // Close the modal when the user clicks anywhere outside of the modal
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});
