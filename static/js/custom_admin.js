// Custom admin interactivity
document.addEventListener('DOMContentLoaded', function() {
    // Example: Confirm deletion
    document.querySelectorAll('.deletelink').forEach(function(element) {
        element.addEventListener('click', function(event) {
            if (!confirm('Are you sure you want to delete this item?')) {
                event.preventDefault();
            }
        });
    });

    // Example: Highlight table rows on hover
    document.querySelectorAll('tr').forEach(function(row) {
        row.addEventListener('mouseover', function() {
            this.style.backgroundColor = '#e9ecef';
        });
        row.addEventListener('mouseout', function() {
            this.style.backgroundColor = '';
        });
    });
});
