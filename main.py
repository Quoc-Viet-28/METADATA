
from fastapi import APIRouter, FastAPI
import importlib
import pkgutil

app = FastAPI()
api_router = APIRouter()


# Hàm tự động load tất cả routers từ thư mục routes
def auto_load_routers(router: APIRouter, package: str):
    # Duyệt qua các module trong package `routes`
    package_path = package.replace('.', '/')
    for module_info in pkgutil.iter_modules([package_path]):
        module_name = f"{package}.{module_info.name}"
        module = importlib.import_module(module_name)

        # Kiểm tra xem module có thuộc tính `router` không
        if hasattr(module, 'router'):
            # Lấy prefix và tags từ module, nếu không có thì dùng giá trị mặc định
            prefix = getattr(module, 'prefix', f"/{module_info.name}")
            tags = getattr(module, 'tags', [module_info.name])
            # Thêm router vào api_router
            router.include_router(
                getattr(module, 'router'),
                prefix=prefix,
                tags=tags
            )


# Gọi hàm auto_load_routers để đăng ký tất cả các router
auto_load_routers(api_router, 'app.routes')

# Đăng ký api_router vào ứng dụng
app.include_router(api_router)
