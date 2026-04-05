from django.db import transaction
from houses.services.house_service import mark_as_rented

def create_contract_workflow(house, creator, tenant_form, contract_form):
    """
    Quy trình xử lý giao dịch Tạo hợp đồng:
    1. Tạo Khách thuê.
    2. Tạo Hợp đồng.
    3. Cập nhật Nhà thành Đã cho thuê.
    Được bọc trong transaction.atomic để đảm bảo tính nhất quán của Database.
    """
    with transaction.atomic():
        # 1. Lưu thông tin người thuê
        tenant = tenant_form.save(commit=False)
        tenant.created_by = creator
        tenant.save()

        # 2. Lưu thông tin hợp đồng
        contract = contract_form.save(commit=False)
        contract.house = house
        contract.renter = tenant
        contract.status = 'active'
        contract.save()

        # 3. Chuyển trạng thái ngôi nhà (Gọi qua HouseService để tuân thủ tính đóng gói)
        mark_as_rented(house)

    return contract, tenant
