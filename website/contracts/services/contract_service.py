from django.db import transaction
from houses.services.house_service import mark_as_rented

def create_contract_workflow(house, creator, tenant_form, contract_form):
    """
    Quy trình xử lý giao dịch Tạo hợp đồng:
    1. Kiểm tra/Tạo Khách thuê (Nếu trùng CCCD của cùng chủ nhà -> Dùng khách cũ & cập nhật thông tin).
    2. Tạo Hợp đồng.
    3. Cập nhật Nhà thành Đã cho thuê.
    """
    with transaction.atomic():
        # 1. Xử lý thông tin người thuê
        cccd = tenant_form.cleaned_data.get('cccd')
        from contracts.models import Tenant
        
        # Tìm xem chủ nhà này đã từng lưu khách có CCCD này chưa
        tenant = Tenant.objects.filter(cccd=cccd, created_by=creator).first()
        
        if tenant:
            # Nếu tồn tại khách cũ, cập nhật thông tin mới từ form
            tenant_form.instance = tenant
            tenant = tenant_form.save()
        else:
            # Nếu là khách mới hoàn toàn
            tenant = tenant_form.save(commit=False)
            tenant.created_by = creator
            tenant.save()

        # 2. Lưu thông tin hợp đồng
        contract = contract_form.save(commit=False)
        contract.house = house
        contract.renter = tenant
        contract.status = 'active'
        contract.save()

        # 3. Chuyển trạng thái ngôi nhà
        mark_as_rented(house)

    return contract, tenant
