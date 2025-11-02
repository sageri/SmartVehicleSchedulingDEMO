# Story 002: VRP最適化エンジン実装

**Story ID:** 002
**Story名:** VRP最適化エンジン実装（VRP Optimization Engine Implementation）
**優先度:** 🔴 High（核心业务功能）
**状态:** 📋 Ready for Development
**依存:** Story 001（✅ 完了）

---

## 📋 Story 概要

**ビジネス価値：**
> 作为AI配车系统的核心功能，实现车辆路径优化（VRP）引擎，使用户能够通过API提交优化请求并获得优化后的配车方案。演示"AI自动配车"如何将配送距离减少25%、成本降低25%。

**技術概要：**
- 使用Google OR-Tools实现CVRPTW（容量约束+时间窗口VRP）
- 同步REST API设计（2-5秒响应时间）
- 完整的数据CRUD API
- 基线对比与改善指标计算

---

## 🎯 ユーザーストーリー

**As a** 物流管理者（Demo演示人员）
**I want to** 通过API执行车辆路径优化计算
**So that** 我可以向客户展示AI如何优化配送路线、降低成本

### 受入条件（Acceptance Criteria）

1. ✅ **演示数据初始化**
   - `POST /api/v1/seed/demo-data` 成功导入100配送点
   - 数据库包含4据点、10车辆、100配送点

2. ✅ **数据查询API**
   - `GET /api/v1/depots` 返回4个据点
   - `GET /api/v1/vehicles` 返回10台车辆（支持depot_id过滤）
   - `GET /api/v1/deliveries` 返回100个配送点（支持time_window过滤）

3. ✅ **VRP优化计算**
   - `POST /api/v1/optimization/optimize` 在10秒内返回结果
   - 返回10条路线（每台车一条）
   - 所有约束条件满足：
     - ✅ 容量不超载（重量+体积）
     - ✅ 时间窗口遵守（早上30%，下午70%）
     - ✅ 每个配送点只访问一次

4. ✅ **基线与改善指标**
   - `baseline_metrics` 包含simple_assignment结果
   - `improvement_metrics` 显示距离削减率 > 20%
   - 成本削减率 > 20%

5. ✅ **性能要求**
   - 优化计算时间：2-5秒（目标），<10秒（上限）
   - API响应时间：GET端点 < 100ms
   - 内存使用：峰值 < 1GB

---

## 📐 技术设计

### アーキテクチャ概要

```
Client Request
    ↓
FastAPI Router (api/v1/)
    ↓
Service Layer (services/)
    ├─ VRPService (核心优化引擎)
    ├─ DataService (数据管理)
    └─ MetricsService (指标计算)
    ↓
Repository Layer (repositories/)
    ├─ DepotRepository
    ├─ VehicleRepository
    └─ DeliveryRepository
    ↓
Database (SQLite)
    └─ Tables: depots, vehicles, deliveries, routes, optimization_results
```

---

### API設計（同期REST）

**核心决策：** 采用同步API（基于`docs/decision-story002-api-algorithm.md`）

#### 端点一览（5个）

| 端点 | 方法 | 功能 | 响应时间 |
|------|-----|------|---------|
| `/api/v1/seed/demo-data` | POST | 初始化演示数据 | ~1秒 |
| `/api/v1/depots` | GET | 获取据点列表 | <100ms |
| `/api/v1/vehicles` | GET | 获取车辆列表 | <100ms |
| `/api/v1/deliveries` | GET | 获取配送点列表 | <100ms |
| `/api/v1/optimization/optimize` | POST | 执行VRP优化 | 2-5秒 |

---

## 📦 タスク分解

### Task 1: 数据模型与数据库Schema（0.5日）

**目标：** 创建SQLAlchemy ORM模型和数据库表

**创建文件：**
```
backend/app/models/
├── __init__.py
├── depot.py          # 据点模型
├── vehicle.py        # 车辆模型
├── delivery.py       # 配送点模型
├── route.py          # 路线模型
└── optimization_result.py  # 优化结果模型
```

**实装内容：**

1. **Depot模型** (`models/depot.py`)
```python
from sqlalchemy import Column, String, Float, Time
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Depot(Base):
    __tablename__ = "depots"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String, nullable=False)
    operating_start_time = Column(Time, nullable=False)
    operating_end_time = Column(Time, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

2. **Vehicle模型** (`models/vehicle.py`)
```python
class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(String, primary_key=True)
    vehicle_type = Column(String, nullable=False)  # "2t" | "4t"
    capacity_weight = Column(Float, nullable=False)
    capacity_volume = Column(Float, nullable=False)
    depot_id = Column(String, ForeignKey("depots.id"))
    available_start_time = Column(Time, nullable=False)
    available_end_time = Column(Time, nullable=False)
    cost_per_km = Column(Float, nullable=False)
    cost_per_hour = Column(Float, nullable=False)

    # Relationship
    depot = relationship("Depot", back_populates="vehicles")
```

3. **Delivery模型** (`models/delivery.py`)
```python
class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(String, primary_key=True)
    customer_name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String, nullable=False)
    package_count = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    time_window = Column(String, nullable=True)  # "morning" | "afternoon" | null
    service_time = Column(Integer, nullable=False)  # minutes
    created_at = Column(DateTime, default=datetime.utcnow)
```

4. **数据库初始化脚本**
```bash
# 创建迁移
alembic init alembic
alembic revision --autogenerate -m "Create initial tables"
alembic upgrade head
```

**验收标准：**
- [ ] 所有模型文件创建完成
- [ ] Alembic迁移生成成功
- [ ] 数据库表创建成功（`backend/data/database.db`）
- [ ] 模型字段与`shared/types/index.ts`一致

---

### Task 2: Pydantic Schema定义（0.5日）

**目标：** 定义API请求/响应的Pydantic schemas

**创建文件：**
```
backend/app/schemas/
├── __init__.py
├── depot.py
├── vehicle.py
├── delivery.py
├── optimization.py  # 优化请求/响应
└── common.py        # 共通schemas
```

**实装示例：**

```python
# schemas/optimization.py
from pydantic import BaseModel
from typing import List, Optional

class OptimizationRequest(BaseModel):
    """VRP优化请求（简化版 - 同步API）"""
    depot_ids: List[str]
    vehicle_ids: List[str]
    delivery_ids: List[str]

class RouteStop(BaseModel):
    """路线停车点"""
    delivery_id: str
    sequence: int
    arrival_time: str  # ISO 8601
    departure_time: str
    distance_from_previous: float  # km
    duration_from_previous: int  # minutes

class Route(BaseModel):
    """配送路线"""
    id: str
    vehicle_id: str
    depot_id: str
    stops: List[RouteStop]
    total_distance: float
    total_duration: int
    total_weight: float
    total_volume: float
    total_cost: float
    utilization_weight: float
    utilization_volume: float

class BaselineMetrics(BaseModel):
    """基线指标（优化前）"""
    total_distance: float
    total_duration: int
    total_cost: float
    average_utilization_weight: float
    method: str = "simple_assignment"

class ImprovementMetrics(BaseModel):
    """改善指标（优化效果）"""
    distance_reduction_km: float
    distance_reduction_percent: float
    duration_reduction_minutes: int
    cost_reduction_amount: float
    cost_reduction_percent: float
    utilization_improvement_percent: float

class OptimizationResult(BaseModel):
    """VRP优化结果"""
    id: str
    request_id: str
    routes: List[Route]
    total_distance: float
    total_duration: int
    total_cost: float
    average_utilization_weight: float
    average_utilization_volume: float
    computation_time: int  # ms
    unassigned_deliveries: List[str]
    baseline_metrics: BaselineMetrics
    improvement_metrics: ImprovementMetrics
    created_at: str  # ISO 8601

    class Config:
        from_attributes = True
```

**验收标准：**
- [ ] 所有schema文件创建完成
- [ ] 字段类型与`shared/types/index.ts`一致
- [ ] Pydantic v2语法正确（`model_config`）
- [ ] FastAPI自动生成OpenAPI文档正确

---

### Task 3: Repository层实装（1日）

**目标：** 实现数据访问层（CRUD操作）

**创建文件：**
```
backend/app/repositories/
├── __init__.py
├── base.py               # 基础Repository
├── depot_repository.py
├── vehicle_repository.py
└── delivery_repository.py
```

**实装示例：**

```python
# repositories/base.py
from sqlalchemy.orm import Session
from typing import Generic, TypeVar, Type, List, Optional

ModelType = TypeVar("ModelType")

class BaseRepository(Generic[ModelType]):
    """基础Repository模式"""

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: str) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self) -> List[ModelType]:
        return self.db.query(self.model).all()

    def create(self, obj: ModelType) -> ModelType:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, id: str) -> bool:
        obj = self.get_by_id(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False

# repositories/vehicle_repository.py
class VehicleRepository(BaseRepository[Vehicle]):
    """车辆Repository"""

    def get_by_depot(self, depot_id: str) -> List[Vehicle]:
        return self.db.query(Vehicle).filter(
            Vehicle.depot_id == depot_id
        ).all()
```

**验收标准：**
- [ ] 所有Repository实现完成
- [ ] 支持基本CRUD操作
- [ ] 支持过滤查询（depot_id, time_window等）
- [ ] 单元测试覆盖率 > 80%

---

### Task 4: VRP优化引擎核心实装（2日）⭐ 最重要

**目标：** 实现OR-Tools VRP求解器

**创建文件：**
```
backend/app/services/
├── __init__.py
├── vrp_service.py        # VRP优化服务 ⭐ 核心
├── baseline_service.py   # 基线计算服务
└── metrics_service.py    # 指标计算服务
```

**核心实装：**

```python
# services/vrp_service.py
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import math

class VRPService:
    """VRP优化服务"""

    def __init__(self):
        self.EARTH_RADIUS = 6371  # km

    def optimize(
        self,
        depots: List[Depot],
        vehicles: List[Vehicle],
        deliveries: List[Delivery]
    ) -> OptimizationResult:
        """
        执行VRP优化计算

        算法：OR-Tools CVRPTW
        - 初始解：PATH_CHEAPEST_ARC
        - 局所探索：GUIDED_LOCAL_SEARCH
        - 时间限制：10秒
        """
        # 1. 准备数据
        data = self._create_data_model(depots, vehicles, deliveries)

        # 2. 创建路由模型
        manager = pywrapcp.RoutingIndexManager(
            len(data['distance_matrix']),
            len(vehicles),
            data['depot_indices']
        )
        routing = pywrapcp.RoutingModel(manager)

        # 3. 定义距离回调
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data['distance_matrix'][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # 4. 添加容量约束
        self._add_capacity_constraints(routing, manager, data, vehicles)

        # 5. 添加时间窗口约束
        self._add_time_window_constraints(routing, manager, data, deliveries)

        # 6. 设置求解参数
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = 10

        # 7. 求解
        start_time = time.time()
        solution = routing.SolveWithParameters(search_parameters)
        computation_time = int((time.time() - start_time) * 1000)

        if not solution:
            raise ValueError("未找到可行解")

        # 8. 提取路线
        routes = self._extract_routes(solution, routing, manager, data, vehicles)

        # 9. 计算基线指标
        baseline = self._calculate_baseline(depots, vehicles, deliveries)

        # 10. 计算改善指标
        improvement = self._calculate_improvement(routes, baseline)

        return OptimizationResult(
            id=str(uuid.uuid4()),
            request_id=str(uuid.uuid4()),
            routes=routes,
            total_distance=sum(r.total_distance for r in routes),
            total_duration=sum(r.total_duration for r in routes),
            total_cost=sum(r.total_cost for r in routes),
            computation_time=computation_time,
            unassigned_deliveries=[],
            baseline_metrics=baseline,
            improvement_metrics=improvement,
            created_at=datetime.utcnow().isoformat()
        )

    def _calculate_haversine_distance(
        self,
        lat1: float, lon1: float,
        lat2: float, lon2: float
    ) -> float:
        """计算两点间的Haversine距离（km）"""
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))

        return self.EARTH_RADIUS * c

    def _add_capacity_constraints(self, routing, manager, data, vehicles):
        """添加车辆容量约束"""
        def demand_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            return data['demands'][from_node]

        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)

        # 重量容量约束
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            [v.capacity_weight for v in vehicles],
            True,  # start cumul to zero
            'Capacity'
        )

    def _add_time_window_constraints(self, routing, manager, data, deliveries):
        """添加时间窗口约束"""
        def time_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data['time_matrix'][from_node][to_node]

        time_callback_index = routing.RegisterTransitCallback(time_callback)

        routing.AddDimension(
            time_callback_index,
            30,   # 等待时间容忍（分钟）
            180,  # 最大路线时间（分钟）
            False,
            'Time'
        )

        time_dimension = routing.GetDimensionOrDie('Time')

        # 设置每个配送点的时间窗口
        for location_idx, time_window in enumerate(data['time_windows']):
            if location_idx == 0:  # 跳过depot
                continue
            index = manager.NodeToIndex(location_idx)
            time_dimension.CumulVar(index).SetRange(
                time_window[0],  # 最早到达时间
                time_window[1]   # 最迟到达时间
            )
```

**验收标准：**
- [ ] VRP求解器正常工作
- [ ] 支持容量约束（重量+体积）
- [ ] 支持时间窗口约束
- [ ] 计算时间 < 10秒（100配送点）
- [ ] 基线计算正确
- [ ] 改善指标计算正确
- [ ] 单元测试覆盖率 > 80%

---

### Task 5: API端点实装（1日）

**目标：** 实现5个REST API端点

**创建文件：**
```
backend/app/api/v1/
├── __init__.py
├── depots.py
├── vehicles.py
├── deliveries.py
├── optimization.py
└── seed.py
```

**实装示例：**

```python
# api/v1/optimization.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.vrp_service import VRPService
from app.schemas.optimization import OptimizationRequest, OptimizationResult

router = APIRouter(prefix="/optimization", tags=["optimization"])

@router.post("/optimize", response_model=OptimizationResult)
async def optimize_routes(
    request: OptimizationRequest,
    db: Session = Depends(get_db)
):
    """
    VRP最適化実行（同期）

    処理時間: 2-5秒（目標）、<10秒（上限）
    """
    try:
        # 1. 加载数据
        depots = [db.query(Depot).get(id) for id in request.depot_ids]
        vehicles = [db.query(Vehicle).get(id) for id in request.vehicle_ids]
        deliveries = [db.query(Delivery).get(id) for id in request.delivery_ids]

        # 2. 验证数据
        if not all(depots) or not all(vehicles) or not all(deliveries):
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INVALID_DATA",
                    "message": "一部のIDが存在しません"
                }
            )

        # 3. 执行优化
        vrp_service = VRPService()
        result = vrp_service.optimize(depots, vehicles, deliveries)

        # 4. 保存结果（可选）
        # db_result = OptimizationResultModel(**result.dict())
        # db.add(db_result)
        # db.commit()

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_REQUEST",
                "message": str(e)
            }
        )
    except TimeoutError:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "OPTIMIZATION_TIMEOUT",
                "message": "最適化計算がタイムアウトしました"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "INTERNAL_ERROR",
                "message": f"内部エラー: {str(e)}"
            }
        )

# api/v1/seed.py
@router.post("/seed/demo-data", status_code=201)
async def seed_demo_data(db: Session = Depends(get_db)):
    """デモデータ初期化"""
    # 1. 清空现有数据
    db.query(Delivery).delete()
    db.query(Vehicle).delete()
    db.query(Depot).delete()

    # 2. 从CSV读取数据
    import csv

    # 读取depots.csv
    with open('data/demo_data/depots.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            depot = Depot(**row)
            db.add(depot)

    # 读取vehicles.csv
    # ...类似处理

    db.commit()

    return {
        "message": "デモデータを初期化しました",
        "summary": {
            "depots": db.query(Depot).count(),
            "vehicles": db.query(Vehicle).count(),
            "deliveries": db.query(Delivery).count()
        }
    }
```

**main.py路由注册：**
```python
# app/main.py
from app.api.v1 import depots, vehicles, deliveries, optimization, seed

app.include_router(depots.router, prefix="/api/v1", tags=["depots"])
app.include_router(vehicles.router, prefix="/api/v1", tags=["vehicles"])
app.include_router(deliveries.router, prefix="/api/v1", tags=["deliveries"])
app.include_router(optimization.router, prefix="/api/v1", tags=["optimization"])
app.include_router(seed.router, prefix="/api/v1", tags=["seed"])
```

**验收标准：**
- [ ] 5个API端点全部实现
- [ ] Swagger UI显示正确
- [ ] 请求验证工作正常
- [ ] 错误处理完整
- [ ] 响应格式符合schema定义

---

### Task 6: 单元测试（1日）

**目标：** 编写单元测试，覆盖率 > 80%

**创建文件：**
```
backend/tests/
├── __init__.py
├── conftest.py           # pytest配置和fixtures
├── services/
│   ├── test_vrp_service.py
│   ├── test_baseline_service.py
│   └── test_metrics_service.py
├── repositories/
│   └── test_repositories.py
└── api/
    └── test_optimization_api.py
```

**测试示例：**

```python
# tests/services/test_vrp_service.py
import pytest
from app.services.vrp_service import VRPService
from app.models import Depot, Vehicle, Delivery

def test_vrp_solver_basic():
    """基本的VRP求解测试"""
    service = VRPService()

    # 准备测试数据
    depot = Depot(
        id="depot-1",
        name="テストデポ",
        latitude=35.6812,
        longitude=139.7671,
        # ...
    )

    vehicles = [
        Vehicle(id="vehicle-1", capacity_weight=2000, ...),
        Vehicle(id="vehicle-2", capacity_weight=2000, ...)
    ]

    deliveries = [
        Delivery(id="delivery-1", weight=100, ...),
        Delivery(id="delivery-2", weight=150, ...),
        Delivery(id="delivery-3", weight=200, ...)
    ]

    # 执行优化
    result = service.optimize([depot], vehicles, deliveries)

    # 断言
    assert len(result.routes) > 0
    assert result.total_distance > 0
    assert result.computation_time < 10000  # < 10秒
    assert result.improvement_metrics.distance_reduction_percent > 0

def test_capacity_constraint():
    """容量制约のテスト"""
    service = VRPService()

    # 创建超重配送点
    heavy_delivery = Delivery(id="d1", weight=3000, ...)  # 超过2000kg容量

    # 应该分配到多台车或报错
    # ...

def test_time_window_constraint():
    """時間窓制約のテスト"""
    # 早上配送点应该只分配到早上时间段
    # ...

# tests/api/test_optimization_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_optimize_api_success():
    """优化API成功测试"""
    response = client.post("/api/v1/optimization/optimize", json={
        "depot_ids": ["depot-1"],
        "vehicle_ids": ["vehicle-1", "vehicle-2"],
        "delivery_ids": ["delivery-1", "delivery-2", "delivery-3"]
    })

    assert response.status_code == 200
    result = response.json()
    assert "routes" in result
    assert "improvement_metrics" in result
    assert result["computation_time"] < 10000

def test_optimize_api_invalid_ids():
    """无效ID测试"""
    response = client.post("/api/v1/optimization/optimize", json={
        "depot_ids": ["invalid-id"],
        "vehicle_ids": [],
        "delivery_ids": []
    })

    assert response.status_code == 400
    assert "error" in response.json() or "detail" in response.json()
```

**验收标准：**
- [ ] 单元测试覆盖率 > 80%
- [ ] 所有测试通过
- [ ] 包含正常场景和异常场景测试
- [ ] 性能测试（计算时间验证）

---

### Task 7: 集成测试（1日）

**目标：** E2E测试完整优化流程

**测试场景：**

```python
# tests/integration/test_full_optimization_flow.py
import pytest
from fastapi.testclient import TestClient

@pytest.mark.asyncio
async def test_full_optimization_workflow():
    """完整な最適化フロー E2Eテスト"""

    # 1. 初始化演示数据
    response = client.post("/api/v1/seed/demo-data")
    assert response.status_code == 201
    summary = response.json()["summary"]
    assert summary["depots"] == 4
    assert summary["vehicles"] == 10
    assert summary["deliveries"] == 100

    # 2. 获取所有据点ID
    response = client.get("/api/v1/depots")
    assert response.status_code == 200
    depots = response.json()["depots"]
    depot_ids = [d["id"] for d in depots]
    assert len(depot_ids) == 4

    # 3. 获取所有车辆ID
    response = client.get("/api/v1/vehicles")
    assert response.status_code == 200
    vehicles = response.json()["vehicles"]
    vehicle_ids = [v["id"] for v in vehicles]
    assert len(vehicle_ids) == 10

    # 4. 获取所有配送点ID
    response = client.get("/api/v1/deliveries")
    assert response.status_code == 200
    deliveries = response.json()["deliveries"]
    delivery_ids = [d["id"] for d in deliveries]
    assert len(delivery_ids) == 100

    # 5. 执行优化
    response = client.post("/api/v1/optimization/optimize", json={
        "depot_ids": depot_ids,
        "vehicle_ids": vehicle_ids,
        "delivery_ids": delivery_ids
    })

    # 6. 验证结果
    assert response.status_code == 200
    result = response.json()

    # 验证路线数量
    assert len(result["routes"]) <= 10  # 最多10条路线
    assert len(result["routes"]) > 0

    # 验证改善指标
    assert result["improvement_metrics"]["distance_reduction_percent"] > 0
    assert result["improvement_metrics"]["cost_reduction_percent"] > 0

    # 验证计算时间
    assert result["computation_time"] < 10000  # < 10秒

    # 验证所有配送点都被分配
    assigned_count = sum(len(r["stops"]) for r in result["routes"])
    assert assigned_count <= 100

    # 验证容量约束
    for route in result["routes"]:
        assert route["utilization_weight"] <= 100.0
        assert route["utilization_volume"] <= 100.0

    print(f"✅ E2E测试通过:")
    print(f"  - 优化路线数: {len(result['routes'])}")
    print(f"  - 距离削减率: {result['improvement_metrics']['distance_reduction_percent']:.1f}%")
    print(f"  - 成本削减率: {result['improvement_metrics']['cost_reduction_percent']:.1f}%")
    print(f"  - 计算时间: {result['computation_time']}ms")
```

**验收标准：**
- [ ] E2E测试流程通过
- [ ] 100配送点优化成功
- [ ] 距离削减率 > 20%
- [ ] 计算时间 < 10秒
- [ ] 所有约束条件满足

---

## 📊 工数見積

| Task | 内容 | 工数 | 累計 |
|------|-----|-----|------|
| Task 1 | 数据模型与Schema | 0.5日 | 0.5日 |
| Task 2 | Pydantic Schema定义 | 0.5日 | 1日 |
| Task 3 | Repository层实装 | 1日 | 2日 |
| Task 4 | VRP优化引擎核心 ⭐ | 2日 | 4日 |
| Task 5 | API端点实装 | 1日 | 5日 |
| Task 6 | 单元测试 | 1日 | 6日 |
| Task 7 | 集成测试 | 1日 | 7日 |
| **合計** | - | **7日** | - |

**缓冲时间：** 1日（处理意外问题）
**总计：** **8日** （约1.5周）

---

## 🚫 非機能要件

### 性能要求

| 指标 | 目标值 | 上限值 |
|-----|--------|--------|
| VRP计算时间（100点） | 2-5秒 | 10秒 |
| GET API响应时间 | <50ms | 100ms |
| POST API响应时间 | 2-5秒 | 10秒 |
| 内存使用（峰值） | <500MB | 1GB |
| 并发支持 | 1用户 | 5用户 |

### 可靠性要求

- [ ] 优化成功率 > 99%（正常数据）
- [ ] 错误处理覆盖所有异常场景
- [ ] 数据验证阻止无效请求

### 可维护性要求

- [ ] 代码覆盖率 > 80%
- [ ] 所有函数有docstring
- [ ] 遵循PEP 8规范（Black格式化）
- [ ] 类型提示完整（mypy兼容）

---

## 🚫 Story 002 不包含的内容

**明确排除（留给后续Story）：**

1. ❌ **前端UI实装** → Story 003（地图可视化）
2. ❌ **地图显示** → Story 003
3. ❌ **结果对比仪表盘** → Story 004
4. ❌ **多算法选择** → 可选的Story 005
5. ❌ **异步任务队列** → 不需要（已决策同步API）
6. ❌ **用户认证** → Demo不需要
7. ❌ **历史记录查询** → Demo不需要
8. ❌ **路线持久化** → 可选功能

---

## ✅ Definition of Done（完成定义）

### 功能完成

- [ ] 所有7个Task完成
- [ ] 5个API端点全部工作
- [ ] VRP优化引擎正常运行
- [ ] 基线与改善指标计算正确

### 质量完成

- [ ] 单元测试覆盖率 > 80%
- [ ] 集成测试通过
- [ ] 代码review通过
- [ ] 无Critical或High severity bug

### 文档完成

- [ ] API文档（Swagger）完整
- [ ] 核心函数有docstring
- [ ] Story 002 README更新

### 性能完成

- [ ] 100配送点优化 < 10秒
- [ ] 距离削减率 > 20%
- [ ] 内存使用 < 1GB

---

## 📝 開発ガイドライン

### コーディング規約

**Python:**
- 遵循PEP 8
- 使用Black格式化
- 使用Ruff检查
- 类型提示完整

**命名规范：**
```python
# 类名：PascalCase
class VRPService:

# 函数名：snake_case
def calculate_distance():

# 常量：UPPER_SNAKE_CASE
EARTH_RADIUS = 6371

# 私有方法：_前缀
def _internal_method():
```

### Git工作流

```bash
# 创建功能分支
git checkout -b feature/story-002-vrp-engine

# 提交规范
git commit -m "feat(vrp): implement OR-Tools solver"
git commit -m "test(vrp): add unit tests for VRP service"
git commit -m "docs(story-002): update API documentation"

# 推送并创建PR
git push origin feature/story-002-vrp-engine
```

---

## 🔗 関連ドキュメント

### 设计文档

- [アーキテクチャ設計](../architecture.md) - 系统整体架构
- [技術決策：API設計とアルゴリズム](../decision-story002-api-algorithm.md) - Story 002决策依据
- [共有型定義](../../shared/types/index.ts) - 前后端共享类型

### 参考资料

- [OR-Tools Documentation](https://developers.google.com/optimization)
- [OR-Tools VRP Guide](https://developers.google.com/optimization/routing)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

---

## 📋 Change Log

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2025-10-31 | 1.0 | Story 002初版作成 | Claude Code |

---

## 🚀 準備状態

**前提条件チェック：**
- ✅ Story 001完了并验证通过
- ✅ Python 3.11虚拟环境就绪
- ✅ OR-Tools 9.8.3296安装成功
- ✅ FastAPI骨架可正常启动
- ✅ 技术决策已确定（同步API、最小算法）

**状态：** ✅ **Ready for Development - 可以立即开始开发！**

---

**次のアクション：** Task 1から開発開始
**予定完了日：** 2025-11-08（8日后）
