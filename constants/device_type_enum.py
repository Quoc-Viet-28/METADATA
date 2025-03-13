from enum import Enum



class DeviceTypeEnum(Enum):
    BOX_AI_DAHUA = "BOX_AI_DAHUA"
    CAMERA_DAHUA_AI = "CAMERA_DAHUA_AI"
    ACCESS_CONTROL_DAHUA = "ACCESS_CONTROL_DAHUA"


LIST_DEVICE_DAHUA = {
    DeviceTypeEnum.BOX_AI_DAHUA: {
        "name": "BOX_AI_DAHUA",
        "channel": "1",
        "events": "TrafficJunction,FaceRecognition,HumanTrait,CrossRegionDetection,CrossLineDetection"
    },
    DeviceTypeEnum.ACCESS_CONTROL_DAHUA: {
        "name": "ACCESS_CONTROL_DAHUA",
        "channel": None,
        "events": "FaceRecognition"
    },
    DeviceTypeEnum.CAMERA_DAHUA_AI: {
        "name": "CAMERA_DAHUA_AI",
        "channel": None,
        "events": "TrafficJunction,TrafficRetrograde,TrafficOverline,TrafficOverSpeed,TrafficNonMotorInMotorRoute,TrafficNonMotorWithoutSafehat,TrafficWithoutSafeBelt,TrafficAssistantWithoutSafeBelt,TrafficDriverSmoking,TrafficDriverCalling,TrafficCrossLane"
    },
}
