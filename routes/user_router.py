from fastapi import APIRouter, Request, Depends

from app.core.security import has_roles, get_user_info, check_role
from app.dto.user_dto import UserCreate, ResetPassword, UserUpdate, AssignRole, EnabledUser
from app.services.user_service import user_service

router = APIRouter()
prefix = "/user"
tags = ["user"]


@router.post("/", dependencies=[Depends(has_roles(["SYSTEM", "ADMIN"]))])
async def create_user(data: UserCreate, user=Depends(get_user_info())):
    """
      - Chỉ có SYSTEM và ADMIN mới được tạo mới user
          + SYSTEM: Có thể tạo user cho bất kỳ công ty nào
          + ADMIN: Chỉ tạo user cho công ty mình quản lý
    """
    return await user_service.create(data, user)


@router.patch("/reset-password")
async def reset_password(data: ResetPassword, user=Depends(get_user_info())):
    return await user_service.reset_password(data, user)


@router.put("/update")
async def update_user(data: UserUpdate, user=Depends(get_user_info())):
    return await user_service.update(data, user)


@router.patch("/assign-role", dependencies=[Depends(has_roles(["SYSTEM", "ADMIN"]))])
async def assign_role(data: AssignRole, user=Depends(get_user_info())):
    return await user_service.assign_role(data, user)


@router.patch("/enable")
async def enable_user(data: EnabledUser, user=Depends(get_user_info())):
    return await user_service.enable_user(data.user_id, user, data.enabled)


@router.get("/", dependencies=[Depends(has_roles(["SYSTEM", "ADMIN"]))])
async def get_user(request: Request, page: int = 0, size: int = 20, search: str = "", enabled=None,
                   user=Depends(get_user_info())):
    token = request.headers.get("Authorization").split(" ")[1]
    __check_role = check_role(user, "SYSTEM")
    if __check_role:
        return await user_service.get_users(token, page, size, search, enabled)
    else:
        return await user_service.get_user_by_company(user, token, page, size)


@router.get("/get-info")
async def get_info_user(user=Depends(get_user_info())):
    return await user_service.get_user_info(user)
