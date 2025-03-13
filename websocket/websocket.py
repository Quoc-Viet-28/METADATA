from fastapi import APIRouter
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.websocket.ConnectionManager import connection_manager
from app.websocket.ConnectionProcessPersonManager import connection_process_person_manager

router = APIRouter()


@router.websocket("/super-admin")
async def websocket_super_admin(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


@router.websocket("/process-person/{id_person}")
async def websocket_process_person(websocket: WebSocket, id_person: str):
    await connection_process_person_manager.connect(websocket, id_person)
    try:
        while True:
            data = await websocket.receive_text()
            # await connection_manager.register_event(websocket, data)
    except WebSocketDisconnect:
        connection_process_person_manager.disconnect(websocket)
@router.websocket("/{company_id}")
async def websocket_endpoint(websocket: WebSocket, company_id: str):
    await connection_manager.connect(websocket, company_id)
    try:
        while True:
            data = await websocket.receive_text()
            # await connection_manager.register_event(websocket, data)
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)

