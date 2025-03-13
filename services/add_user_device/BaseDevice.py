class BaseDevice:
    def __init__(self, type_name=None):
        self.type_name = type_name

    async def create(self, device, person, group_id=None):
        pass

    async def create_person_existed(self, device, person, person_camera, group_id=None):
        return False, "Người này đã tồn tại trên thiết bị"

    async def delete_person(self, person_camera, device, person):
        pass

    async def update(self, person_camera, is_update_image=False):
        pass
