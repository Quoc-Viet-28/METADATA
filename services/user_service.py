import asyncio

from fastapi import HTTPException, status
from keycloak import KeycloakAdmin

from app.core.security import check_role, get_company, check_roles
from app.core.setting_env import settings
from app.dto.user_dto import UserCreate, UserUpdate, AssignRole, ResetPassword
from app.models.profile_model import Profile
from app.utils.call_api_httpx import get_data_auth, post_data_auth


class UserService:
    def __init__(self):
        self.keycloak_admin = KeycloakAdmin(server_url=settings.URL_KEYCLOAK,
                                            client_id=settings.CLIENT_ID_KEYCLOAK,
                                            realm_name=settings.REALM_KEYCLOAK,
                                            client_secret_key=settings.CLIENT_SECRET_KEYCLOAK)

    async def create(self, data: UserCreate, user):
        try:
            company = await get_company(user, data.id_company)
            new_user = await asyncio.to_thread(self.keycloak_admin.create_user, {"email": data.email,
                                                                                 "username": data.username,
                                                                                 "enabled": True,
                                                                                 "firstName": "",
                                                                                 "lastName": data.full_name,
                                                                                 "credentials": [
                                                                                     {"value": data.password,
                                                                                      "type": "password", }]})
            profile = Profile(id_user=new_user, company=company)
            await profile.insert()
            return {"id": new_user, **data.dict(), "company": company.dict()}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def check_role_user(self, user, _id_user):
        __check_role = check_roles(user, ["SYSTEM", "ADMIN"])
        user_id = user["sub"]
        if __check_role:
            user_id = _id_user
            if check_role(user, "ADMIN"):
                profile = await Profile.find_one({"id_user": user_id})
                if profile is None:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail="Không thể reset password cho user này")
                company = await profile.company.fetch()
                if company.id != user["company"].id:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail="Không thể reset password cho user này")
        return user_id

    async def update(self, data: UserUpdate, user):
        try:
            payload = data.dict(exclude_unset=True, exclude={"id_company", "id_user"})
            company = await get_company(user, data.id_company)

            id_user = await self.check_role_user(user, data.id_user)

            await asyncio.to_thread(self.keycloak_admin.update_user, id_user, payload)
            if data.id_company and company:
                profile = await Profile.find_one({"id_user": id_user})
                if profile:
                    profile.company = company
                    await profile.replace()
                else:
                    profile = Profile(id_user=id_user, company=company)
                    await profile.insert()
            return {"message": "Update user success"}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def reset_password(self, data: ResetPassword, user):
        try:
            user_id = await self.check_role_user(user, data.user_id)

            await asyncio.to_thread(self.keycloak_admin.set_user_password, user_id, data.password, data.temporary)
            return {"message": "Reset password success"}

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def get_role(self, list_roles):
        # lấy ra name
        data = [role['name'] for role in list_roles]
        if "SYSTEM_ORYZA_METADATA" in data:
            return 0
        if "ADMIN_ORYZA_METADATA" in data:
            return 1
        return 2

    async def assign_role(self, data: AssignRole, user):
        if data.role.endswith("_ORYZA_METADATA") is False:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không thể gán role này")
        if data.user_id == user["sub"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không thể gán role cho chính mình")

        _list_role = await asyncio.to_thread(self.keycloak_admin.get_realm_roles_of_user, user["sub"])
        list_roles = await asyncio.to_thread(self.keycloak_admin.get_realm_roles_of_user, data.user_id)
        _role = self.get_role(_list_role)
        role = self.get_role(list_roles)
        if _role == role:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bạn đang bằng quyền với user này")

        if _role == 1 and data.role == "SYSTEM_ORYZA_METADATA":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không thể gán role này")

        if _role == 1:
            profile = await Profile.find_one({"id_user": data.user_id})
            if profile is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không thể gán role cho user này")
            company = await profile.company.fetch()
            if company.id != user["company"].id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User không thuộc công ty của bạn")

        try:
            res = await asyncio.to_thread(self.keycloak_admin.get_realm_role, data.role)
            await asyncio.to_thread(self.keycloak_admin.assign_realm_roles, data.user_id, [res])
            for role in list_roles:
                if role["name"] != data.role and role["name"].endswith("_ORYZA_METADATA"):
                    await asyncio.to_thread(self.keycloak_admin.delete_realm_roles_of_user, data.user_id, [role])
            return {"message": "Assign role success"}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def enable_user(self, user_id: str, user, enabled: bool = True):
        try:
            id_user = await self.check_role_user(user, user_id)
            await asyncio.to_thread(self.keycloak_admin.update_user, id_user, {"enabled": enabled})
            return {"message": "Enable user success"}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def get_users(self, token: str, page: int = 0, size: int = 20, search: str = None, enabled=None):
        try:
            url = f"{settings.URL_KEYCLOAK}/realms/{settings.REALM_KEYCLOAK}/my-rest-resource/admin/users"
            result = await get_data_auth(url=url, headers={"Authorization": f"Bearer {token}"},
                                         params={"size": size, "search": search, "page": page, "enabled": enabled})
            result = result.json()

            ids = [user["id"] for user in result["content"]]
            profiles = await Profile.find({"id_user": {"$in": ids}}).to_list(length=len(ids))
            for user in result["content"]:
                profile = next((profile for profile in profiles if profile.id_user == user["id"]), None)
                user["company"] = None
                user["updated_at"] = None
                if profile:
                    user["updated_at"] = profile.updated_at
                    data = await profile.company.fetch()
                    user["company"] = {"name": data.name, "id": str(data.id)}

            return result
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def get_user_by_company(self, user, token, page: int = 0, size: int = 20, id_company=None, search=None,
                                  enabled=None):
        company = await get_company(user, id_company)

        data = await Profile.find(Profile.company.id == company.id).skip(page * size).limit(size).to_list()
        totalPages = await Profile.find(Profile.company.id == company.id).count()
        ids = [profile.id_user for profile in data]
        url = f"{settings.URL_KEYCLOAK}/realms/{settings.REALM_KEYCLOAK}/my-rest-resource/admin/users/find-by-list-user-id"
        result = await post_data_auth(url=url, headers={"Authorization": f"Bearer {token}"}, json={"ids": ids})
        result = result.json()
        # print("result", result)
        for _user in result:
            profile = next((profile for profile in data if profile.id_user == _user["id"]), None)
            _user["company"] = None
            _user["updated_at"] = None
            if profile:
                _user["updated_at"] = profile.updated_at
                company = await profile.company.fetch()
                _user["company"] = {"name": company.name, "id": str(company.id)}
        return {"content": result, "page": page, "size": size, "totalElements": len(data),
                "totalPages": totalPages // size + 1}

    async def get_user_info(self, user):
        try:
            res = await asyncio.to_thread(self.keycloak_admin.get_user, user["sub"])
            res["company"] = {
                "id": str(user["company"].id) if user["company"] else None,
                "name": str(user["company"].name) if user["company"] else None
            }
            return res
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


user_service = UserService()
