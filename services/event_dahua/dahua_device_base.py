import re
import time

from app.constants.device_type_enum import LIST_DEVICE_DAHUA
from app.models.device_model import Device
from app.services.event_dahua.text_helper import parse_event_data


class DahuaDeviceBase():

    def __init__(self):
        pass

    def set_device(self, device: Device):
        self.buffer = b""
        self.device = device
        self.boundary = b"\r\n--myboundary\r\n"

    def set_url(self):
        EVENT_TEMPLATE = "{protocol}://{host}:{port}/cgi-bin/snapManager.cgi?action=attachFileProc{channel}&heartbeat=5&Flags[0]=Event&Events=[{events}]"
        # self.EVENT_TEMPLATE = "{protocol}://{host}:{port}/cgi-bin/mediaFileFind.cgi?action=findFile&condition.Channel=7&condition.Events[0]=TrafficJunction"
        data = LIST_DEVICE_DAHUA.get(self.device.device_type)
        channel = data.get("channel")

        self.url = EVENT_TEMPLATE.format(
            protocol=self.device.protocol,
            host=self.device.ip_device,
            port=self.device.port,
            events=data.get("events"),
            channel="&channel=" + channel if channel else "",
        )
        # print(self.url)
        return self.url

    async def save_data(self, data, image):
        # print(data)
        return None

    # on receive data from camera.
    async def on_receive(self, data):
        self.buffer += data
        while True:
            start_index = self.buffer.find(self.boundary)
            if start_index == -1:
                break

            end_index = self.buffer.find(
                self.boundary, start_index + len(self.boundary)
            )
            if end_index == -1:
                # End boundary not found, check if we can extract content length
                header_end_index = self.buffer.find(b"\r\n\r\n") + 4
                if header_end_index > 4:
                    headers = self.buffer[:header_end_index].decode("utf-8")
                    content_length_match = re.search(r"Content-Length: (\d+)", headers)
                    if content_length_match:
                        content_length = int(content_length_match.group(1))
                        if len(self.buffer) >= header_end_index + content_length:
                            # We have a complete message based on content length
                            message = self.buffer[: header_end_index + content_length]
                            await self.process_message(message)
                            self.buffer = self.buffer[
                                          header_end_index + content_length:
                                          ]
                            continue
                # If we reach here, we don't have enough data to process; break to wait for more
                break

            # If end boundary is found, process as before
            message = self.buffer[start_index:end_index]
            await self.process_message(message)
            self.buffer = self.buffer[end_index:]

    async def process_message(self, message):
        header_end_index = message.find(b"\r\n\r\n") + 4
        headers = message[:header_end_index].decode("utf-8")
        content_type_match = re.search(r"Content-Type: ([\w/]+)", headers)
        content_length_match = re.search(r"Content-Length: (\d+)", headers)
        if content_type_match and content_length_match:
            content_type = content_type_match.group(1)
            content_length = int(content_length_match.group(1))
            actual_content = message[
                             header_end_index: header_end_index + content_length
                             ]
            if content_type == "text/plain":
                self.data_text = parse_event_data(actual_content)
            elif content_type == "image/jpeg":
                try:
                    data_text = self.data_text.copy()
                    __data_result = await self.save_data(data_text, actual_content)
                except Exception as e:
                    print("Error save data", e)
