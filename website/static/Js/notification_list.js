document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.getElementById('toggle-delete-mode');
    const checkboxes = document.querySelectorAll('.delete-checkbox');
    const deleteBtn = document.getElementById('delete-selected-btn');
    let deleteMode = false;
    
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            deleteMode = !deleteMode;
            checkboxes.forEach(cb => cb.style.display = deleteMode ? 'inline-block' : 'none');
            if (deleteBtn) deleteBtn.style.display = deleteMode ? 'inline-block' : 'none';
            toggleBtn.innerHTML = deleteMode ? '<i class="bi bi-x-circle me-1"></i> Hủy' : '<i class="bi bi-list-check me-1"></i> Chọn để xóa';
            if(deleteMode) {
                toggleBtn.classList.replace('btn-outline-secondary', 'btn-secondary');
            } else {
                toggleBtn.classList.replace('btn-secondary', 'btn-outline-secondary');
                checkboxes.forEach(cb => cb.checked = false);
            }
        });
    }
});
