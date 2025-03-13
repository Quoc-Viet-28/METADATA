from fastapi import WebSocket


class ConnectionProcessPersonManager:
    active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, id_person):
        await websocket.accept()
        if id_person in self.active_connections:
            self.active_connections[id_person].append(websocket)
        else:
            self.active_connections[id_person] = [websocket]

    def disconnect(self, websocket: WebSocket):
        for key, value in self.active_connections.items():
            if websocket in value:
                value.remove(websocket)
                if not value:  # Remove the key if the list is empty
                    del self.active_connections[key]
                break

    async def send_message_json(self, list, message: dict):
        for id_person in list:
            if id_person in self.active_connections:
                for connection in self.active_connections[id_person]:
                    try:
                        await connection.send_json(message)
                    except Exception as e:
                        print("send_message_json", e)


connection_process_person_manager = ConnectionProcessPersonManager()
