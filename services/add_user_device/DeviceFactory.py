
import importlib
import pkgutil
import os

class DeviceFactory:
    class_registry = {}

    @classmethod
    def register_class(cls, type_names):
        # Decorator để đăng ký class với nhiều type_name
        def wrapper(class_type):
            # Đăng ký class cho từng type_name trong danh sách
            for type_name in type_names:
                cls.class_registry[type_name] = class_type
            return class_type

        return wrapper

    @classmethod
    def add_class(cls, type_name):
        if type_name in cls.class_registry:
            return cls.class_registry[type_name](type_name=type_name)
        else:
            raise ValueError(f"Type '{type_name}' không được hỗ trợ.")

    @classmethod
    def auto_import_classes(cls, package_name):
        package_dir = os.path.join(os.path.dirname(__file__), package_name)
        for _, module_name, _ in pkgutil.iter_modules([package_dir]):
            importlib.import_module(f"app.services.add_user_device.{package_name}.{module_name}")
DeviceFactory.auto_import_classes("classes")
