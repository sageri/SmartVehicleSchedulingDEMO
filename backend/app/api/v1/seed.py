"""
AI自動配車システムデモプロトタイプ - Seed API

デモデータを生成するエンドポイントを提供します。
Epic 005: 多拠点・大規模配送先データ生成対応
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import time
from typing import List, Tuple, Dict, Any, Optional
import math
import random

from app.database import get_db
from app.models import Depot, Vehicle, Delivery
from app.repositories import DepotRepository, VehicleRepository, DeliveryRepository
from app.schemas.common import MessageResponse

router = APIRouter()

# Epic 005: 2拠点の定義（Story 5.1.1: 陸地制約強化）
DEPOT_CONFIGS = [
    {
        "id": "depot-tokyo",
        "name": "東京デポ",
        "latitude": 35.6812,
        "longitude": 139.7671,
        "address": "東京都千代田区丸の内1-1-1",
    },
    {
        "id": "depot-saitama",
        "name": "さいたま市デポ",
        "latitude": 35.8617,
        "longitude": 139.6455,
        "address": "埼玉県さいたま市大宮区桜木町1-1-1",
    },
]

# Epic 005: 車両配分（2拠点・5台、Story 5.1.1: さいたま市対応）
VEHICLE_ALLOCATION = {
    "depot-tokyo": {
        "2t": ["vehicle-101", "vehicle-102"],
        "4t": ["vehicle-201"],
    },
    "depot-saitama": {
        "2t": ["vehicle-103", "vehicle-104"],
    },
}

# Epic 005: 車両タイプ別仕様
VEHICLE_SPECS = {
    "2t": {
        "capacity_weight": 2000.0,
        "capacity_volume": 10.0,
        "cost_per_km": 50.0,
        "cost_per_hour": 2000.0,
    },
    "4t": {
        "capacity_weight": 4000.0,
        "capacity_volume": 20.0,
        "cost_per_km": 80.0,
        "cost_per_hour": 3000.0,
    },
}

# Epic 005: データ生成設定（Story 5.1.1: 東京20件・さいたま10件に変更）
DELIVERIES_PER_DEPOT = {
    "depot-tokyo": 20,  # 東京デポ周辺20件
    "depot-saitama": 10,  # さいたま市デポ周辺10件
}
MAX_DELIVERY_RADIUS_KM = 50.0  # 使用されない（固定リストのため）
PACKAGE_COUNT_WEIGHTS = [0.5, 0.35, 0.15]  # 1枚:50%, 2枚:35%, 3枚:15%
TIME_WINDOW_WEIGHTS = [0.2, 0.3, 0.5]  # 午前:20%, 午後:30%, 指定なし:50% - Epic 005: VRP解探索性向上のため柔軟性を強化

# Story 5.1.1: 固定配送先リスト（実際の地点を使用、ランダム生成を廃止）
FIXED_DELIVERY_LOCATIONS = {
    "depot-tokyo": [
        # 東京都内の実際の地点（20件）
        {"name": "新宿区役所", "latitude": 35.6938, "longitude": 139.7034},
        {"name": "渋谷駅周辺", "latitude": 35.6580, "longitude": 139.7016},
        {"name": "池袋サンシャインシティ", "latitude": 35.7295, "longitude": 139.7190},
        {"name": "上野公園", "latitude": 35.7148, "longitude": 139.7740},
        {"name": "品川駅周辺", "latitude": 35.6284, "longitude": 139.7387},
        {"name": "六本木ヒルズ", "latitude": 35.6604, "longitude": 139.7292},
        {"name": "秋葉原電気街", "latitude": 35.6983, "longitude": 139.7731},
        {"name": "吉祥寺駅周辺", "latitude": 35.7032, "longitude": 139.5797},
        {"name": "立川市役所", "latitude": 35.7143, "longitude": 139.4079},
        {"name": "町田市役所", "latitude": 35.5474, "longitude": 139.4267},
        {"name": "八王子駅周辺", "latitude": 35.6559, "longitude": 139.3388},
        {"name": "三鷹市役所", "latitude": 35.6832, "longitude": 139.5597},
        {"name": "調布市役所", "latitude": 35.6535, "longitude": 139.5419},
        {"name": "府中市役所", "latitude": 35.6688, "longitude": 139.4777},
        {"name": "多摩センター駅", "latitude": 35.6244, "longitude": 139.4285},
        {"name": "錦糸町駅周辺", "latitude": 35.6969, "longitude": 139.8136},
        {"name": "北千住駅周辺", "latitude": 35.7489, "longitude": 139.8048},
        {"name": "赤羽駅周辺", "latitude": 35.7774, "longitude": 139.7209},
        {"name": "国分寺市役所", "latitude": 35.7102, "longitude": 139.4620},
        {"name": "小平市役所", "latitude": 35.7284, "longitude": 139.4774},
    ],
    "depot-saitama": [
        # 埼玉県内の実際の地点（10件）
        {"name": "さいたま新都心", "latitude": 35.8944, "longitude": 139.6306},
        {"name": "浦和駅周辺", "latitude": 35.8617, "longitude": 139.6589},
        {"name": "川口市役所", "latitude": 35.8078, "longitude": 139.7242},
        {"name": "川越市役所", "latitude": 35.9253, "longitude": 139.4857},
        {"name": "所沢駅周辺", "latitude": 35.7991, "longitude": 139.4689},
        {"name": "越谷レイクタウン", "latitude": 35.8784, "longitude": 139.8233},
        {"name": "春日部市役所", "latitude": 35.9757, "longitude": 139.7531},
        {"name": "久喜市役所", "latitude": 36.0625, "longitude": 139.6669},
        {"name": "蓮田市役所", "latitude": 35.9942, "longitude": 139.6603},
        {"name": "上尾市役所", "latitude": 35.9771, "longitude": 139.5933},
    ],
}


def calculate_destination_point(
    lat: float, lon: float, distance_km: float, bearing_rad: float
) -> Tuple[float, float]:
    """
    Haversine逆変換: 出発点・距離・方位から目的地座標を計算

    Args:
        lat: 出発点の緯度（度）
        lon: 出発点の経度（度）
        distance_km: 移動距離（km）
        bearing_rad: 方位角（ラジアン、0=北）

    Returns:
        Tuple[float, float]: 目的地の(緯度, 経度)

    Reference:
        https://www.movable-type.co.uk/scripts/latlong.html
    """
    EARTH_RADIUS_KM = 6371.0
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)

    angular_distance = distance_km / EARTH_RADIUS_KM

    dest_lat_rad = math.asin(
        math.sin(lat_rad) * math.cos(angular_distance)
        + math.cos(lat_rad) * math.sin(angular_distance) * math.cos(bearing_rad)
    )

    dest_lon_rad = lon_rad + math.atan2(
        math.sin(bearing_rad) * math.sin(angular_distance) * math.cos(lat_rad),
        math.cos(angular_distance) - math.sin(lat_rad) * math.sin(dest_lat_rad),
    )

    return math.degrees(dest_lat_rad), math.degrees(dest_lon_rad)


def calculate_haversine_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """
    Haversine距離計算: 2点間の距離を計算（km）

    Args:
        lat1, lon1: 地点1の緯度・経度（度）
        lat2, lon2: 地点2の緯度・経度（度）

    Returns:
        float: 距離（km）
    """
    EARTH_RADIUS_KM = 6371.0

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_KM * c


def generate_deliveries_around_depot(
    depot_config: Dict[str, Any],
    count: int,
    max_radius_km: float,
    start_index: int,
    seed: Optional[int] = None,
) -> List[Delivery]:
    """
    指定した拠点の周辺に配送先を生成（Story 5.1.1: 固定リストを使用）

    Args:
        depot_config: 拠点の設定情報（id, name, latitude, longitude）
        count: 生成する配送先数（例: 15件）
        max_radius_km: 使用されない（固定リストのため）
        start_index: 配送先IDの開始インデックス
        seed: ランダムシード値（伝票枚数・時間指定のランダム生成用）

    Returns:
        List[Delivery]: 生成された配送先リスト
    """
    deliveries = []
    depot_id = depot_config["id"]

    # シード値を設定（伝票枚数・時間指定のランダム生成用）
    if seed is not None:
        random.seed(seed)

    # 固定配送先リストを取得
    fixed_locations = FIXED_DELIVERY_LOCATIONS.get(depot_id, [])

    # 要求された件数分の配送先を生成（最大で固定リストの件数まで）
    for i in range(min(count, len(fixed_locations))):
        location = fixed_locations[i]

        # 伝票枚数を重み付きランダムで決定（1枚:50%, 2枚:35%, 3枚:15%）
        num_packages = random.choices([1, 2, 3], weights=PACKAGE_COUNT_WEIGHTS)[0]

        # 時間指定を分布に従って決定（午前:20%, 午後:30%, 指定なし:50%）
        time_window = random.choices(
            ["morning", "afternoon", None], weights=TIME_WINDOW_WEIGHTS
        )[0]

        # 配送先IDの生成（例: delivery-0001）
        delivery_id = f"delivery-{start_index + i + 1:04d}"

        deliveries.append(
            Delivery(
                id=delivery_id,
                customer_name=location["name"],
                latitude=location["latitude"],
                longitude=location["longitude"],
                address=f"{location['name']}",
                package_count=num_packages,
                weight=10.0 * num_packages,  # 1伝票あたり10kg
                volume=0.5 * num_packages,  # 1伝票あたり0.5m³
                time_window=time_window,
                service_time=15,  # 15分固定
                depot_id=depot_id,  # Epic 005: Multi-Depot対応 - 配送先と拠点を関連付け
            )
        )

    return deliveries


def validate_data_distribution(
    depots: List[Depot], deliveries: List[Delivery]
) -> Dict[str, Any]:
    """
    生成されたデータの分布を検証

    Args:
        depots: 拠点リスト
        deliveries: 配送先リスト

    Returns:
        Dict: バリデーション結果
            - depot_distances_valid: bool
            - max_depot_distance_km: float
            - delivery_distances_valid: bool
            - package_distribution: dict
            - time_window_distribution: dict
    """
    # 1. 拠点間距離の検証（全て20km圏内か？）
    max_depot_distance = 0.0
    for i, depot_a in enumerate(depots):
        for depot_b in depots[i + 1 :]:
            dist = calculate_haversine_distance(
                depot_a.latitude,
                depot_a.longitude,
                depot_b.latitude,
                depot_b.longitude,
            )
            max_depot_distance = max(max_depot_distance, dist)

    depot_distances_valid = max_depot_distance <= 20.0

    # 2. 配送先の分布検証（各拠点から50km圏内か？）
    delivery_distances_valid = True
    max_delivery_distance = 0.0
    for delivery in deliveries:
        # 最寄り拠点を探す
        min_dist = float("inf")
        for depot in depots:
            dist = calculate_haversine_distance(
                depot.latitude, depot.longitude, delivery.latitude, delivery.longitude
            )
            min_dist = min(min_dist, dist)
        max_delivery_distance = max(max_delivery_distance, min_dist)
        if min_dist > 50.0:
            delivery_distances_valid = False

    # 3. 伝票枚数分布の検証（50%/35%/15%に近いか？）
    package_counts = [d.package_count for d in deliveries]
    total_count = len(deliveries)
    package_distribution = {
        1: round(package_counts.count(1) / total_count * 100, 1),
        2: round(package_counts.count(2) / total_count * 100, 1),
        3: round(package_counts.count(3) / total_count * 100, 1),
    }

    # 4. 時間指定分布の検証（30%/60%/10%に近いか？）
    time_windows = [d.time_window for d in deliveries]
    time_window_distribution = {
        "morning": round(time_windows.count("morning") / total_count * 100, 1),
        "afternoon": round(time_windows.count("afternoon") / total_count * 100, 1),
        "none": round(time_windows.count(None) / total_count * 100, 1),
    }

    return {
        "depot_distances_valid": depot_distances_valid,
        "max_depot_distance_km": round(max_depot_distance, 2),
        "delivery_distances_valid": delivery_distances_valid,
        "max_delivery_distance_km": round(max_delivery_distance, 2),
        "package_distribution": package_distribution,
        "time_window_distribution": time_window_distribution,
    }


@router.post("/demo-data", response_model=MessageResponse, status_code=201)
def create_demo_data(db: Session = Depends(get_db), seed: Optional[int] = 42):
    """
    デモデータを生成（Epic 005: 2拠点・30配送先・5台車両）

    既存のデータを全て削除し、新しいデモデータを作成します。

    Args:
        seed: ランダムシード値（デフォルト: 42、固定値で再現可能）
              Noneの場合: 完全ランダム（毎回異なるデータ生成）

    Returns:
        MessageResponse: 生成結果メッセージ
    """
    depot_repo = DepotRepository(db)
    vehicle_repo = VehicleRepository(db)
    delivery_repo = DeliveryRepository(db)

    # シード値を固定（テストやデバッグ時の再現性確保）
    if seed is not None:
        random.seed(seed)

    # 既存データを削除
    delivery_repo.delete_all()
    vehicle_repo.delete_all()
    depot_repo.delete_all()

    # ===== Phase 1: 拠点作成（2拠点） =====
    depots = []
    for depot_config in DEPOT_CONFIGS:
        depot = Depot(
            id=depot_config["id"],
            name=depot_config["name"],
            latitude=depot_config["latitude"],
            longitude=depot_config["longitude"],
            address=depot_config["address"],
            operating_start_time=time(8, 0),
            operating_end_time=time(18, 0),
        )
        depot_repo.create(depot)
        depots.append(depot)

    # ===== Phase 1 (Story 5.2): 車両作成（5台） =====
    vehicles = []
    for depot in depots:
        allocation = VEHICLE_ALLOCATION.get(depot.id, {})

        # 2t車を生成
        for vehicle_id in allocation.get("2t", []):
            vehicle = Vehicle(
                id=vehicle_id,
                vehicle_type="2t",
                capacity_weight=VEHICLE_SPECS["2t"]["capacity_weight"],
                capacity_volume=VEHICLE_SPECS["2t"]["capacity_volume"],
                depot_id=depot.id,
                available_start_time=time(8, 0),
                available_end_time=time(18, 0),
                cost_per_km=VEHICLE_SPECS["2t"]["cost_per_km"],
                cost_per_hour=VEHICLE_SPECS["2t"]["cost_per_hour"],
            )
            vehicle_repo.create(vehicle)
            vehicles.append(vehicle)

        # 4t車を生成
        for vehicle_id in allocation.get("4t", []):
            vehicle = Vehicle(
                id=vehicle_id,
                vehicle_type="4t",
                capacity_weight=VEHICLE_SPECS["4t"]["capacity_weight"],
                capacity_volume=VEHICLE_SPECS["4t"]["capacity_volume"],
                depot_id=depot.id,
                available_start_time=time(8, 0),
                available_end_time=time(18, 0),
                cost_per_km=VEHICLE_SPECS["4t"]["cost_per_km"],
                cost_per_hour=VEHICLE_SPECS["4t"]["cost_per_hour"],
            )
            vehicle_repo.create(vehicle)
            vehicles.append(vehicle)

    # ===== Phase 2: 配送先作成（30件、陸地制約対応） =====
    all_deliveries = []
    cumulative_index = 0
    for depot_config in DEPOT_CONFIGS:
        depot_id = depot_config["id"]
        count = DELIVERIES_PER_DEPOT[depot_id]

        depot_deliveries = generate_deliveries_around_depot(
            depot_config=depot_config,
            count=count,
            max_radius_km=MAX_DELIVERY_RADIUS_KM,
            start_index=cumulative_index,
            seed=None,  # 各拠点で異なるランダム生成（グローバルseedで制御）
        )
        all_deliveries.extend(depot_deliveries)
        cumulative_index += count

    for delivery in all_deliveries:
        delivery_repo.create(delivery)

    # ===== Phase 4: バリデーション =====
    validation_result = validate_data_distribution(depots, all_deliveries)

    # バリデーション結果を詳細メッセージに含める
    detail = (
        f"拠点: {len(depots)}件, 車両: {len(vehicles)}台, 配送先: {len(all_deliveries)}件 | "
        f"拠点間距離: {validation_result['max_depot_distance_km']}km (Valid: {validation_result['depot_distances_valid']}) | "
        f"配送先距離: {validation_result['max_delivery_distance_km']}km (Valid: {validation_result['delivery_distances_valid']}) | "
        f"伝票枚数分布: 1枚={validation_result['package_distribution'][1]}%, 2枚={validation_result['package_distribution'][2]}%, 3枚={validation_result['package_distribution'][3]}% | "
        f"時間指定分布: 午前={validation_result['time_window_distribution']['morning']}%, 午後={validation_result['time_window_distribution']['afternoon']}%, 指定なし={validation_result['time_window_distribution']['none']}%"
    )

    return MessageResponse(
        message="デモデータを作成しました（Epic 005: 2拠点・30配送先・5台車両）",
        detail=detail,
    )
