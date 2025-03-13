from fastapi import WebSocket


class ConnectionManager:
    active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, company_id):
        await websocket.accept()
        if company_id in self.active_connections:
            self.active_connections[company_id].append(websocket)
        else:
            self.active_connections[company_id] = [websocket]

    def disconnect(self, websocket: WebSocket):
        for key, value in self.active_connections.items():
            if websocket in value:
                value.remove(websocket)
                break

    async def send_company_message_json(self, company_id: str, message: dict):
        list_id_company = [company_id, "super_admin"]
        for id_company in list_id_company:
            if id_company in self.active_connections:
                for connection in self.active_connections[id_company]:
                    await connection.send_json(message)


connection_manager = ConnectionManager()
