// Initialize DataTables for the repoTable
$(document).ready(function() {
    $('#repoTable').DataTable({
        "paging": false,      // Disable DataTables pagination
        "searching": true,    // Enable search
        "ordering": true,     // Enable column ordering
        "info": false,        // Disable table info
        "autoWidth": false,   // Disable auto column width calculation
    });
});