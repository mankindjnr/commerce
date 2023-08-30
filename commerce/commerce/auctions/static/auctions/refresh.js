function refreshPage() {
    location.reload(); // This reloads the current page
}

document.addEventListener('DOMContentLoaded', function() {
    let watchlistForm = document.getElementById('watchlistForm');
    
    watchlistForm.addEventListener('submit', function(event) {
        // Prevent the default form submission behavior
        event.preventDefault();
        
        // Submit the form using AJAX/Fetch
        let formData = new FormData(watchlistForm);
        fetch(watchlistForm.action, {
            method: 'POST',
            body: formData
        }).then(function(response) {
            // Handle successful form submission if needed
            
            // Refresh the page after a short delay
            setTimeout(function() {
                location.reload();
            }, 1000); // Refresh after 1 second (adjust as needed)
        }).catch(function(error) {
            // Handle fetch errors if needed
        });
    });
});