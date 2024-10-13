/**
 * JavaScript code to handle the display of the delete post modal.
 * 
 * This script listens for the DOMContentLoaded event, ensuring that the 
 * DOM is fully loaded before executing the code. It selects the delete 
 * post button and initializes the Bootstrap modal for deleting posts. 
 * When the delete post button is clicked, the delete post modal is displayed.
 */
document.addEventListener('DOMContentLoaded', function () {

    const deletePostButton = document.querySelector('.btn-danger[data-bs-target="#deletePostModal"]');
    const deletePostModal = new bootstrap.Modal(document.getElementById('deletePostModal'));
    if (deletePostButton) {
        deletePostButton.addEventListener('click', function () {
            deletePostModal.show();
        });
    }
});