"""
AI自動配車システムデモプロトタイプ - アプリケーション設定

環境変数とアプリケーション設定を管理します。
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """
    アプリケーション設定クラス

    環境変数または .env ファイルから設定を読み込みます。
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # アプリケーション設定
    APP_NAME: str = "AI自動配車システム"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # データベース設定
    DATABASE_URL: str = "sqlite:///./data/database.db"

    # CORS設定
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",  # Vite開発サーバー
        "http://localhost:3000",  # 代替フロントエンドポート
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # VRP最適化設定
    VRP_TIME_LIMIT_SECONDS: int = 600  # 最適化計算の最大時間（秒）- Epic 005: 100件配送先対応のため10分に拡張
    VRP_SOLUTION_LIMIT: int = 1000     # 解探索の最大数

    # デモデータ設定
    DEMO_DATA_PATH: str = "./data/demo_data"


# グローバル設定インスタンス
settings = Settings()
