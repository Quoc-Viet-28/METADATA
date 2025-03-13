from app.constants.device_type_enum import DeviceTypeEnum
from app.services.event_dahua.dahua_device_base import DahuaDeviceBase
from app.services.event_dahua.device_dahua_factory import DeviceDahuaFactory
from app.services.event_dahua.event_handler.event_handler_camera_ai_factory import EventHandlerCameraAIFactory
@DeviceDahuaFactory.register_class(DeviceTypeEnum.CAMERA_DAHUA_AI)
class CameraAiDahuaDevice(DahuaDeviceBase):
    def __init__(self):
        super().__init__()

    async def save_data(self, data, image):
        event_name = data.get('EventBaseInfo', {}).get('Code', 'Unknown')
        eventHandlerCameraAIFactory = EventHandlerCameraAIFactory.add_class(event_name)
        return await eventHandlerCameraAIFactory.save(data, image, self.device)
