document.addEventListener('DOMContentLoaded', function() {
    const btnUpload = document.getElementById('btn-trigger-upload');
    const avatarInput = document.querySelector('input[name="avatar"]');
    const avatarImage = document.querySelector('.profile-avatar-image');
    const dashboardAvatar = document.querySelector('.dashboard-avatar-image');
    
    const cropperModalEl = document.getElementById('cropperModal');
    let cropperModal = null;
    if (cropperModalEl) {
        cropperModal = new bootstrap.Modal(cropperModalEl);
    }
    const cropperImage = document.getElementById('cropper-image');
    const btnCropSave = document.getElementById('btn-crop-save');
    
    let cropper = null;
    let originalFileName = "avatar.jpg";
    let originalFileType = "image/jpeg";

    if (btnUpload && avatarInput) {
        // Use a hidden temporary input to trigger the file dialog
        const tempInput = document.createElement('input');
        tempInput.type = 'file';
        tempInput.accept = 'image/*';
        
        btnUpload.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            tempInput.value = '';
            tempInput.click();
        }, true);

        tempInput.addEventListener('change', function(e) {
            if (this.files && this.files[0]) {
                const file = this.files[0];
                originalFileName = file.name;
                originalFileType = file.type;
                
                const reader = new FileReader();
                reader.onload = function(evt) {
                    if (cropperImage) {
                        cropperImage.src = evt.target.result;
                        if (cropperModal) cropperModal.show();
                    }
                }
                reader.readAsDataURL(file);
            }
        });
        
        if (cropperModalEl) {
            cropperModalEl.addEventListener('shown.bs.modal', function () {
                if (cropper) {
                    cropper.destroy();
                }
                if (cropperImage) {
                    cropper = new Cropper(cropperImage, {
                        aspectRatio: 1,
                        viewMode: 1,
                        dragMode: 'move',
                        autoCropArea: 0.9,
                        restore: false,
                        guides: false,
                        center: false,
                        highlight: false,
                        cropBoxMovable: true,
                        cropBoxResizable: true,
                        toggleDragModeOnDblclick: false,
                    });
                }
            });

            cropperModalEl.addEventListener('hidden.bs.modal', function () {
                if (cropper) {
                    cropper.destroy();
                    cropper = null;
                }
            });
        }

        if (btnCropSave) {
            btnCropSave.addEventListener('click', function() {
                if (!cropper) return;
                
                const canvas = cropper.getCroppedCanvas({
                    width: 400,
                    height: 400,
                    imageSmoothingEnabled: true,
                    imageSmoothingQuality: 'high',
                });
                
                canvas.toBlob(function(blob) {
                    const url = URL.createObjectURL(blob);
                    if (avatarImage) avatarImage.src = url;
                    if (dashboardAvatar) dashboardAvatar.src = url;
                    
                    const croppedFile = new File([blob], originalFileName, {
                        type: originalFileType,
                        lastModified: new Date().getTime()
                    });
                    
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(croppedFile);
                    avatarInput.files = dataTransfer.files;
                    
                    if (cropperModal) cropperModal.hide();
                }, originalFileType, 0.9);
            });
        }
    }
});
