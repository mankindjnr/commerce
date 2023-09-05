function refreshPage() {
    location.reload(); // This reloads the current page
}

$(document).ready(function() {
    $("#commentsForm").on("submit", function(event) {
        event.preventDefault();  // Prevent the default form submission

        var form = $(this);
        var url = form.data("url");

        $.ajax({
            type: "POST",
            url: url,
            data: form.serialize(),  // Serialize the form data
            success: function(data) {
                // Assuming the server returns the updated comment HTML
                $("#commentsContainer").html(data);

                // Clear the textarea
                form.find("textarea").val("");
            },
            error: function(xhr, status, error) {
                console.error(xhr.responseText);
            }
        });
    });
});
