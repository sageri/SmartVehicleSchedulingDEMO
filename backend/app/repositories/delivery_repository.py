"""
AI自動配車システムデモプロトタイプ - 配送先Repository
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Literal

from app.models.delivery import Delivery
from app.repositories.base import BaseRepository


class DeliveryRepository(BaseRepository[Delivery]):
    """
    配送先（Delivery）データアクセスクラス

    配送先の検索・CRUD操作を提供します。
    """

    def __init__(self, db: Session):
        """
        Args:
            db: データベースセッション
        """
        super().__init__(Delivery, db)

    def get_by_time_window(
        self, time_window: Optional[Literal["morning", "afternoon"]]
    ) -> List[Delivery]:
        """
        時間窓で検索

        Args:
            time_window: 時間窓（"morning" | "afternoon" | None）

        Returns:
            List[Delivery]: 該当する配送先リスト
        """
        return self.db.query(Delivery).filter(Delivery.time_window == time_window).all()

    def get_by_ids(self, delivery_ids: List[str]) -> List[Delivery]:
        """
        複数の配送先IDで一括取得

        Args:
            delivery_ids: 配送先IDリスト

        Returns:
            List[Delivery]: 配送先リスト
        """
        return self.db.query(Delivery).filter(Delivery.id.in_(delivery_ids)).all()

    def search_by_customer_name(self, customer_name: str) -> List[Delivery]:
        """
        顧客名で部分一致検索

        Args:
            customer_name: 顧客名（部分一致）

        Returns:
            List[Delivery]: 該当する配送先リスト
        """
        return (
            self.db.query(Delivery)
            .filter(Delivery.customer_name.like(f"%{customer_name}%"))
            .all()
        )

    def search_by_location(
        self, min_lat: float, max_lat: float, min_lon: float, max_lon: float
    ) -> List[Delivery]:
        """
        位置範囲で検索

        Args:
            min_lat: 最小緯度
            max_lat: 最大緯度
            min_lon: 最小経度
            max_lon: 最大経度

        Returns:
            List[Delivery]: 範囲内の配送先リスト
        """
        return (
            self.db.query(Delivery)
            .filter(Delivery.latitude >= min_lat)
            .filter(Delivery.latitude <= max_lat)
            .filter(Delivery.longitude >= min_lon)
            .filter(Delivery.longitude <= max_lon)
            .all()
        )

    def get_by_weight_range(self, min_weight: float, max_weight: float) -> List[Delivery]:
        """
        重量範囲で検索

        Args:
            min_weight: 最小重量（kg）
            max_weight: 最大重量（kg）

        Returns:
            List[Delivery]: 該当する配送先リスト
        """
        return (
            self.db.query(Delivery)
            .filter(Delivery.weight >= min_weight)
            .filter(Delivery.weight <= max_weight)
            .all()
        )

    def count_by_time_window(
        self, time_window: Optional[Literal["morning", "afternoon"]]
    ) -> int:
        """
        時間窓ごとの配送先数をカウント

        Args:
            time_window: 時間窓

        Returns:
            int: 配送先数
        """
        return self.db.query(Delivery).filter(Delivery.time_window == time_window).count()

    def get_statistics(self) -> dict:
        """
        配送先の統計情報を取得

        Returns:
            dict: 統計情報
                - total: 総配送先数
                - morning: 午前配送数
                - afternoon: 午後配送数
                - anytime: 時間指定なし配送数
                - avg_weight: 平均重量（kg）
                - total_weight: 総重量（kg）
        """
        from sqlalchemy import func

        total = self.db.query(Delivery).count()
        morning = self.count_by_time_window("morning")
        afternoon = self.count_by_time_window("afternoon")
        anytime = self.count_by_time_window(None)

        weight_stats = self.db.query(
            func.avg(Delivery.weight).label("avg_weight"),
            func.sum(Delivery.weight).label("total_weight"),
        ).first()

        return {
            "total": total,
            "morning": morning,
            "afternoon": afternoon,
            "anytime": anytime,
            "avg_weight": float(weight_stats.avg_weight) if weight_stats.avg_weight else 0.0,
            "total_weight": float(weight_stats.total_weight) if weight_stats.total_weight else 0.0,
        }
