import typing

from fastapi import Depends, HTTPException, status
from fastapi_keycloak_middleware import get_user

from app.models.company_model import Company
from app.models.profile_model import Profile


def has_role(role_name: str):
    role_name = role_name + "_ORYZA_METADATA"

    async def check_role(user=Depends(get_user)):
        roles = user["realm_access"]["roles"]
        if role_name not in roles:
            raise HTTPException(status_code=403, detail="Unauthorized access")
        return user

    return check_role


def has_roles(roles: typing.List[str]):
    async def check_role(user=Depends(get_user)):
        user_roles = user["realm_access"]["roles"]
        check = False
        for role in roles:
            role = role + "_ORYZA_METADATA"
            if role in user_roles:
                check = True
                break
        if not check:
            raise HTTPException(status_code=403, detail="Unauthorized access")
        return user

    return check_role


def get_user_info():
    async def _get_user(user=Depends(get_user)):
        data = await Profile.find_one({"id_user": user["sub"]})
        user["company"] = None
        if data:
            company = await data.company.fetch()
            user["company"] = company
        return user

    return _get_user


def check_role(user, role_name: str):
    role_name = role_name + "_ORYZA_METADATA"
    roles = user["realm_access"]["roles"]
    return role_name in roles


def check_roles(user, roles: typing.List[str]):
    user_roles = user["realm_access"]["roles"]
    check = False
    for role in roles:
        role = role + "_ORYZA_METADATA"
        if role in user_roles:
            check = True
            break
    return check


async def get_company(user, id_company):
    __check_role = check_role(user, "SYSTEM")
    """
        # neu tai khoan la SYSTEM thi lay cong ty tu id_company
        # neu khong thi lay cong ty tu user
    """
    if __check_role:
        company = await Company.find_one({"_id": id_company})
        if not company:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không tìm thấy công ty")
    else:
        company = user["company"]
        if company is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Tài khoản hiện tại chưa được gán công ty, vui lòng liên hệ admin để được hỗ trợ")
    return company
