
from app.constants.device_type_enum import DeviceTypeEnum
from app.services.event_dahua.dahua_device_base import DahuaDeviceBase
from app.services.event_dahua.device_dahua_factory import  DeviceDahuaFactory
from app.services.event_dahua.event_handler.event_handler_box_ai_factory import EventHandlerBoxAIFactory

@DeviceDahuaFactory.register_class(DeviceTypeEnum.BOX_AI_DAHUA)
class BoxAIDahuaDevice(DahuaDeviceBase):

    def __init__(self):
        super().__init__()


    async def save_data(self, data, image):
        # direction_flow=data.get('Direction', None)
        # with open(f'CRS_TEST_{direction_flow}.json', 'w') as f:
        #     json.dump(data, f, indent=4)
        event_name = data.get('EventBaseInfo', {}).get('Code', 'Unknown')
        eventHandlerBoxAIFactory = EventHandlerBoxAIFactory.add_class(event_name)
        return await eventHandlerBoxAIFactory.save(data, image, self.device)
