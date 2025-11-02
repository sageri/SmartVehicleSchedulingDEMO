"""
AI自動配車システムデモプロトタイプ - データベース接続管理

SQLAlchemy セッション管理と Base クラスを提供します。
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.config import settings

# SQLAlchemy エンジン作成
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite用（マルチスレッド対応）
    echo=settings.DEBUG,  # SQLログを出力（デバッグ時）
)

# セッションファクトリ
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ORM Base クラス
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    データベースセッションを取得する依存性注入関数

    FastAPI の Depends() で使用します。

    Yields:
        Session: SQLAlchemy セッション

    Example:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    データベースを初期化（全テーブル作成）

    Note:
        本番環境では Alembic マイグレーションを使用することを推奨します。
        このメソッドは開発・デモ用途です。
    """
    # すべてのモデルをインポート（Base.metadata に登録するため）
    from app.models import depot, vehicle, delivery, route, optimization_result  # noqa: F401

    # すべてのテーブルを作成
    Base.metadata.create_all(bind=engine)
    print(f"✅ データベース初期化完了: {settings.DATABASE_URL}")
