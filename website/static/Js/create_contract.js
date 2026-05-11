document.addEventListener('DOMContentLoaded', function() {
    const tenantSelectEl = document.getElementById('existingTenantSelect');
    if (tenantSelectEl) {
        // 1. Khởi tạo Choices.js
        const choices = new Choices(tenantSelectEl, {
            searchEnabled: true,
            searchPlaceholderValue: 'Tìm theo tên, SĐT...',
            itemSelectText: 'Nhấn để chọn',
            noResultsText: 'Không tìm thấy khách này',
            noChoicesText: 'Danh sách trống',
            shouldSort: false,
        });

        // 2. Lắng nghe sự kiện thay đổi qua Choices.js
        tenantSelectEl.addEventListener('change', function(event) {
            const selectedId = event.detail.value;
            
            if (!selectedId || selectedId === "") {
                // Reset form
                document.getElementsByName('full_name')[0].value = "";
                document.getElementsByName('phone')[0].value = "";
                document.getElementsByName('cccd')[0].value = "";
                document.getElementsByName('gender')[0].value = "male";
                document.getElementsByName('dob')[0].value = "";
                document.getElementsByName('address')[0].value = "";
            } else {
                // Lấy option gốc để lấy data attributes
                const option = Array.from(tenantSelectEl.options).find(opt => opt.value == selectedId);
                if (option) {
                    document.getElementsByName('full_name')[0].value = option.getAttribute('data-fullname') || "";
                    document.getElementsByName('phone')[0].value = option.getAttribute('data-phone') || "";
                    document.getElementsByName('cccd')[0].value = option.getAttribute('data-cccd') || "";
                    document.getElementsByName('gender')[0].value = option.getAttribute('data-gender') || "male";
                    document.getElementsByName('dob')[0].value = option.getAttribute('data-dob') || "";
                    document.getElementsByName('address')[0].value = option.getAttribute('data-address') || "";
                }
            }
        });
    }
});
