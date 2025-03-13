import asyncio
import time

import httpx
import pycurl

from app.constants.device_status_enum import DeviceStatusEnum
from app.models.device_model import Device
from app.services.event_dahua.device_dahua_factory import DeviceDahuaFactory
from app.websocket.ConnectionManager import connection_manager


class DahuaEventThread():
    """Connects to device and subscribes to events"""
    # Danh sách các kết nối
    active_tasks = {}
    failed_connections = []

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DahuaEventThread, cls).__new__(cls)
        return cls.instance

    async def send_status_device(self, company_id, status, device_id):
        await connection_manager.send_company_message_json(str(company_id), {
            "type": "status_device",
            "data": {
                "device_id": str(device_id),
                "status": str(status.value),
            }
        })

    async def add_device(self, device: Device, is_reconnect=False):
        device_factory = DeviceDahuaFactory.add_class(device.device_type)
        device_factory.set_device(device)
        url = device_factory.set_url()
        if is_reconnect is False:
            device.status = DeviceStatusEnum.START
            await device.replace()
            await self.send_status_device(str(device.company.id), DeviceStatusEnum.START, device.id)
        try:

            async with httpx.AsyncClient(auth=httpx.DigestAuth(device.user_name, device.password),
                                         timeout=30) as client:
                async with client.stream("GET", url) as response:
                    device.status = DeviceStatusEnum.ONLINE
                    await device.replace()
                    async for chunk in response.aiter_bytes():
                        if chunk.startswith(b"Error") and chunk.find(b"RmLogin") != -1:
                            device.status = DeviceStatusEnum.LOCK
                            await device.replace()
                            await self.send_status_device(str(device.company.id), DeviceStatusEnum.LOCK, device.id)

                        elif chunk.find(b"Error\r\nInvalid Authority!\r\n") != -1:
                            device.status = DeviceStatusEnum.ERROR_AUTHORITY
                            await device.replace()
                            await self.send_status_device(str(device.company.id), DeviceStatusEnum.ERROR_AUTHORITY,
                                                          device.id)

                        elif chunk.find(b"Error\r\nBad Request!\r\n") != -1:
                            device.status = DeviceStatusEnum.ERROR_BAD_REQUEST
                            await device.replace()
                            await self.send_status_device(str(device.company.id), DeviceStatusEnum.ERROR_BAD_REQUEST,
                                                          device.id)

                        else:
                            await device_factory.on_receive(chunk)
        except Exception as e:
            if device.status == DeviceStatusEnum.ONLINE:
                device.status = DeviceStatusEnum.ERROR_CONNECTION
                await self.send_status_device(str(device.company.id), DeviceStatusEnum.ERROR_CONNECTION, device.id)
            elif str(e).find("getaddrinfo failed") != -1:
                # print("IP không đúng định dạng")
                device.status = DeviceStatusEnum.ERROR_IP
                await self.send_status_device(str(device.company.id), DeviceStatusEnum.ERROR_IP, device.id)
            else:
                device.status = DeviceStatusEnum.START_FAIL
                await self.send_status_device(str(device.company.id), DeviceStatusEnum.START_FAIL, device.id)

            await device.replace()
            # print(f"Connection {device.id} failed: {e}")
        self.failed_connections.append(device.id)
        # print(f"Connection {device.id} failed permanently.")

    def remove_device(self, device_id):
        if device_id in self.active_tasks:
            self.active_tasks[device_id].cancel()
            del self.active_tasks[device_id]
            print(f"Connection {device_id} removed.")

        if device_id in self.failed_connections:
            self.failed_connections.remove(device_id)
            print(f"Connection {device_id} removed from failed connections.")

    async def monitor_failed_connections(self):
        """
        Kiểm tra và kết nối lại các kết nối bị lỗi định kỳ.
        """
        while True:
            try:
                for connection_id in self.failed_connections:
                    # print(f"Retrying failed connection {connection_id}...")
                    device = await Device.get(connection_id, fetch_links=True)
                    if device is not None \
                            and device.status != DeviceStatusEnum.STOP \
                            and device.status != DeviceStatusEnum.ERROR_AUTHORITY \
                            and device.status != DeviceStatusEnum.ERROR_BAD_REQUEST \
                            and device.status != DeviceStatusEnum.ERROR_IP:
                        task = asyncio.create_task(self.add_device(device=device, is_reconnect=True))
                        self.active_tasks[connection_id] = task
                    self.failed_connections.remove(connection_id)
                await asyncio.sleep(10)  # Chạy kiểm tra mỗi 10 giây
            except Exception as e:
                print(f"Error in monitor_failed_connections: {e}")

    async def load_initial_connections(self, ):
        """
        Đọc dữ liệu từ database và khởi động các kết nối ban đầu.
        """
        list_device = await Device.find(fetch_links=True).to_list()
        print("Loading initial connections from database...")
        for device in list_device:
            if device.status != DeviceStatusEnum.STOP:
                task = asyncio.create_task(self.add_device(device=device))
                self.active_tasks[device.id] = task
        print("All initial connections started.")
