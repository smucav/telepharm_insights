from pydantic import BaseModel
from typing import List, Optional


class TopProduct(BaseModel):
    product: str
    mention_count: int


class ChannelActivity(BaseModel):
    date_id: str
    message_count: int
    image_count: int
    object_detections: List[dict]


class MessageSearch(BaseModel):
    message_id: str
    channel_name: str
    message_date: str
    text: str
