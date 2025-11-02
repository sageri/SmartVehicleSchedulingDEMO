"""
AI自動配車システムデモプロトタイプ - 拠点Repository
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.depot import Depot
from app.repositories.base import BaseRepository


class DepotRepository(BaseRepository[Depot]):
    """
    拠点（Depot）データアクセスクラス

    拠点の検索・CRUD操作を提供します。
    """

    def __init__(self, db: Session):
        """
        Args:
            db: データベースセッション
        """
        super().__init__(Depot, db)

    def get_by_name(self, name: str) -> Optional[Depot]:
        """
        拠点名で検索

        Args:
            name: 拠点名

        Returns:
            Optional[Depot]: 拠点（存在しない場合はNone）
        """
        return self.db.query(Depot).filter(Depot.name == name).first()

    def get_by_ids(self, depot_ids: List[str]) -> List[Depot]:
        """
        複数の拠点IDで一括取得

        Args:
            depot_ids: 拠点IDリスト

        Returns:
            List[Depot]: 拠点リスト
        """
        return self.db.query(Depot).filter(Depot.id.in_(depot_ids)).all()

    def search_by_location(
        self, min_lat: float, max_lat: float, min_lon: float, max_lon: float
    ) -> List[Depot]:
        """
        位置範囲で検索

        Args:
            min_lat: 最小緯度
            max_lat: 最大緯度
            min_lon: 最小経度
            max_lon: 最大経度

        Returns:
            List[Depot]: 範囲内の拠点リスト
        """
        return (
            self.db.query(Depot)
            .filter(Depot.latitude >= min_lat)
            .filter(Depot.latitude <= max_lat)
            .filter(Depot.longitude >= min_lon)
            .filter(Depot.longitude <= max_lon)
            .all()
        )
