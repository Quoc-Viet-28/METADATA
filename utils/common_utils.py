from fastapi import HTTPException,status

from app.core.security import check_role
from app.models.company_model import Company


async def get_company(user, id_company):
    __check_role = check_role(user, "SYSTEM")
    if user["company"] is None and __check_role is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền truy cập dữ liệu"
        )
    if __check_role:
        company = await Company.find_one({"_id": id_company})

    else:
        company = user["company"]

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy công ty"
        )
    return company
