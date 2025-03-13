import importlib
import pkgutil
import os



class DeviceDahuaFactory:
    class_registry = {}

    @classmethod
    def register_class(cls, type_name):
        # Decorator để đăng ký class với type_name
        def wrapper(class_type):
            cls.class_registry[type_name] = class_type
            return class_type

        return wrapper

    @classmethod
    def add_class(cls, type_name):
        if type_name in cls.class_registry:
            return cls.class_registry[type_name]()
        else:
            print(f"Type '{type_name}' không được hỗ trợ.")
            raise ValueError(f"Type '{type_name}' không được hỗ trợ.")

    @classmethod
    def auto_import_classes(cls, package_name):
        package_dir = os.path.join(os.path.dirname(__file__), package_name)
        for _, module_name, _ in pkgutil.iter_modules([package_dir]):
            importlib.import_module(f"app.services.event_dahua.{package_name}.{module_name}")


DeviceDahuaFactory.auto_import_classes("classes")
