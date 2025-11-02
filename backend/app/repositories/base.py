"""
AI自動配車システムデモプロトタイプ - 基底Repositoryクラス

すべてのRepositoryクラスの基底クラスを提供します。
Generic型を使用してDRYの原則を適用します。
"""

from sqlalchemy.orm import Session
from typing import Generic, TypeVar, Type, List, Optional, Any, Dict

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """
    基底Repositoryクラス

    CRUD操作の共通実装を提供します。

    Type Parameters:
        ModelType: SQLAlchemy ORM モデルの型

    Example:
        class UserRepository(BaseRepository[User]):
            def __init__(self, db: Session):
                super().__init__(User, db)
    """

    def __init__(self, model: Type[ModelType], db: Session):
        """
        Args:
            model: SQLAlchemy ORM モデルクラス
            db: データベースセッション
        """
        self.model = model
        self.db = db

    def get_by_id(self, id: str) -> Optional[ModelType]:
        """
        IDでレコードを取得

        Args:
            id: レコードID

        Returns:
            Optional[ModelType]: レコード（存在しない場合はNone）
        """
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        すべてのレコードを取得

        Args:
            skip: スキップする件数（ページネーション用）
            limit: 最大取得件数

        Returns:
            List[ModelType]: レコードリスト
        """
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        レコード数をカウント

        Args:
            filters: フィルタ条件（key: カラム名, value: 値）

        Returns:
            int: レコード数
        """
        query = self.db.query(self.model)
        if filters:
            for key, value in filters.items():
                query = query.filter(getattr(self.model, key) == value)
        return query.count()

    def create(self, obj: ModelType) -> ModelType:
        """
        レコードを作成

        Args:
            obj: 作成するORM モデルインスタンス

        Returns:
            ModelType: 作成されたレコード（DB反映済み）
        """
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj: ModelType) -> ModelType:
        """
        レコードを更新

        Args:
            obj: 更新するORM モデルインスタンス（既にフィールドが更新済み）

        Returns:
            ModelType: 更新されたレコード（DB反映済み）
        """
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, id: str) -> bool:
        """
        IDでレコードを削除

        Args:
            id: レコードID

        Returns:
            bool: 削除成功時True、レコードが存在しない場合False
        """
        obj = self.get_by_id(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False

    def delete_all(self) -> int:
        """
        すべてのレコードを削除（⚠️ 危険操作）

        Returns:
            int: 削除されたレコード数
        """
        count = self.db.query(self.model).count()
        self.db.query(self.model).delete()
        self.db.commit()
        return count

    def exists(self, id: str) -> bool:
        """
        IDのレコードが存在するか確認

        Args:
            id: レコードID

        Returns:
            bool: 存在する場合True
        """
        return self.db.query(self.model).filter(self.model.id == id).count() > 0
