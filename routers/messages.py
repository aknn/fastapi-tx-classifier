from fastapi import APIRouter, Body
from typing import Dict
from models import MsgPayload, MsgRequestPayload

router = APIRouter(prefix="/messages", tags=["messages"])

# In-memory store for messages
messages_list: dict[int, MsgPayload] = {}


@router.post(
    "/",
    response_model=Dict[str, MsgPayload],
    status_code=201,
    summary="Add a new message from request body",
)
def add_msg(payload: MsgRequestPayload = Body(...)) -> Dict[str, MsgPayload]:
    msg_id = max(messages_list.keys()) + 1 if messages_list else 0
    new_message = MsgPayload(msg_id=msg_id, msg_name=payload.msg_name)
    messages_list[msg_id] = new_message
    return {"message": new_message}


@router.get(
    "/",
    response_model=Dict[str, Dict[int, MsgPayload]],
    summary="List all messages",
)
def message_items() -> Dict[str, Dict[int, MsgPayload]]:
    return {"messages": messages_list}
