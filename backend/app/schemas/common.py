"""
AI自動配車システムデモプロトタイプ - 共通Schemas
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional


class MessageResponse(BaseModel):
    """
    汎用メッセージレスポンス

    Example:
        {
            "message": "処理が完了しました",
            "detail": "100件のデータを作成しました"
        }
    """

    message: str
    detail: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "処理が完了しました",
                "detail": "100件のデータを作成しました",
            }
        }
    )


class ErrorDetail(BaseModel):
    """
    エラー詳細レスポンス

    FastAPI HTTPException の detail に使用します。

    Example:
        {
            "code": "INVALID_REQUEST",
            "message": "リクエストが無効です",
            "details": "depot_ids は必須です"
        }
    """

    code: str
    message: str
    details: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "INVALID_REQUEST",
                "message": "リクエストが無効です",
                "details": "depot_ids は必須です",
            }
        }
    )
