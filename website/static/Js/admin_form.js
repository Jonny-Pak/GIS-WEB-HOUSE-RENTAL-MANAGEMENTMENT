document.addEventListener('DOMContentLoaded', function () {
    // 1. CKEditor Initialization
    var textareas = document.querySelectorAll('textarea.ckeditor-content');
    textareas.forEach(function (textarea) {
        if (typeof CKEDITOR !== 'undefined') {
            CKEDITOR.replace(textarea.id, {
                height: 400,
                language: 'vi',
                removePlugins: 'elementspath',
                resize_enabled: false
            });
        }
    });

    // 2. Leaflet Map Initialization
    var mapEl = document.getElementById('admin-house-map');
    if (mapEl && typeof L !== 'undefined') {
        var lat = parseFloat(mapEl.getAttribute('data-lat'));
        var lng = parseFloat(mapEl.getAttribute('data-lng'));
        var name = mapEl.getAttribute('data-name');
        var address = mapEl.getAttribute('data-address');

        if (!isNaN(lat) && !isNaN(lng)) {
            var map = L.map('admin-house-map').setView([lat, lng], 16);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors',
                maxZoom: 19
            }).addTo(map);
            L.marker([lat, lng]).addTo(map)
                .bindPopup('<strong>' + name + '</strong><br>' + address)
                .openPopup();
        }
    }

    // 3. Image Delete Handler
    document.querySelectorAll('.admin-image-delete-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            if (confirm('Xóa ảnh chi tiết này?')) {
                var action = this.getAttribute('data-action');
                var csrf = this.getAttribute('data-csrf');

                var f = document.createElement('form');
                f.method = 'post';
                f.action = action;

                var c = document.createElement('input');
                c.type = 'hidden';
                c.name = 'csrfmiddlewaretoken';
                c.value = csrf;

                f.appendChild(c);
                document.body.appendChild(f);
                f.submit();
            }
        });
    });
});
