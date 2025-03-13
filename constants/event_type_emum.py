from enum import Enum


class EventTypeEnum(Enum):
    FACE = "FACE"
    METADATA = "METADATA"
    TRAFFIC = "TRAFFIC"
    CROSS_LINE = "CROSSLINE"
    CROSS_REGION = "CROSSREGION"