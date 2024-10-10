document.addEventListener('DOMContentLoaded', function () {

    const deletePostButton = document.querySelector('.btn-danger[data-bs-target="#deletePostModal"]');
    const deletePostModal = new bootstrap.Modal(document.getElementById('deletePostModal'));
    if (deletePostButton) {
        deletePostButton.addEventListener('click', function () {
            deletePostModal.show();
        });
    }
});