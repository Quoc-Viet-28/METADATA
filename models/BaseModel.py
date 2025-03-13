from beanie import Document, before_event, Replace
from pydantic import Field
from datetime import datetime
from typing import Optional


class BaseModel(Document):
    created_at: datetime = Field(default_factory=datetime.now)  # Automatically set on creation
    updated_at: Optional[datetime] = None  # Updated when saving

    # Hook Beanie để tự động cập nhật `updated_at` trước khi lưu tài liệu
    @before_event(Replace)
    async def update_timestamp(self):
        self.updated_at = datetime.now()  # Cập nhật trường `updated_at` với thời gian hiện tại
