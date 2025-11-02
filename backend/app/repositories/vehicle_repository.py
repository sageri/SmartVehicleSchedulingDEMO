"""
AI自動配車システムデモプロトタイプ - 車両Repository
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Literal

from app.models.vehicle import Vehicle
from app.repositories.base import BaseRepository


class VehicleRepository(BaseRepository[Vehicle]):
    """
    車両（Vehicle）データアクセスクラス

    車両の検索・CRUD操作を提供します。
    """

    def __init__(self, db: Session):
        """
        Args:
            db: データベースセッション
        """
        super().__init__(Vehicle, db)

    def get_by_depot(self, depot_id: str) -> List[Vehicle]:
        """
        拠点IDで車両を検索

        Args:
            depot_id: 拠点ID

        Returns:
            List[Vehicle]: 該当拠点の車両リスト
        """
        return self.db.query(Vehicle).filter(Vehicle.depot_id == depot_id).all()

    def get_by_type(self, vehicle_type: Literal["2t", "4t"]) -> List[Vehicle]:
        """
        車両タイプで検索

        Args:
            vehicle_type: 車両タイプ（"2t" または "4t"）

        Returns:
            List[Vehicle]: 該当タイプの車両リスト
        """
        return self.db.query(Vehicle).filter(Vehicle.vehicle_type == vehicle_type).all()

    def get_by_ids(self, vehicle_ids: List[str]) -> List[Vehicle]:
        """
        複数の車両IDで一括取得

        Args:
            vehicle_ids: 車両IDリスト

        Returns:
            List[Vehicle]: 車両リスト
        """
        return self.db.query(Vehicle).filter(Vehicle.id.in_(vehicle_ids)).all()

    def get_by_depot_and_type(
        self, depot_id: str, vehicle_type: Literal["2t", "4t"]
    ) -> List[Vehicle]:
        """
        拠点IDと車両タイプで検索

        Args:
            depot_id: 拠点ID
            vehicle_type: 車両タイプ

        Returns:
            List[Vehicle]: 該当する車両リスト
        """
        return (
            self.db.query(Vehicle)
            .filter(Vehicle.depot_id == depot_id)
            .filter(Vehicle.vehicle_type == vehicle_type)
            .all()
        )

    def count_by_depot(self, depot_id: str) -> int:
        """
        拠点の車両数をカウント

        Args:
            depot_id: 拠点ID

        Returns:
            int: 車両数
        """
        return self.db.query(Vehicle).filter(Vehicle.depot_id == depot_id).count()
