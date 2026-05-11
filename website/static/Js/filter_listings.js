function exportExcel() {
    const dateFrom = document.getElementById('date_from').value;
    const dateTo   = document.getElementById('date_to').value;
    if (!dateFrom || !dateTo) { 
        alert('Vui lòng chọn khoảng thời gian.'); 
        return; 
    }
    const baseUrl = window.location.pathname;
    const url = baseUrl + "?date_from=" + dateFrom + "&date_to=" + dateTo + "&export=1";
    window.location.href = url;
}
