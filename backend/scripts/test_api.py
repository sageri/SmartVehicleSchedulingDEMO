"""
API エンドポイントテストスクリプト

FastAPI サーバーに対して HTTP リクエストを送信し、
すべてのエンドポイントをテストします。
"""

import sys
from pathlib import Path
import requests
import json

# プロジェクトルートを sys.path に追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

BASE_URL = "http://localhost:8000"


def print_section(title):
    """セクションヘッダーを出力"""
    print("\n" + "=" * 70)
    print(f"📋 {title}")
    print("=" * 70)


def test_api():
    """APIエンドポイントをテスト"""

    print("=" * 70)
    print("🚀 API エンドポイントテスト")
    print("=" * 70)
    print(f"\nベースURL: {BASE_URL}")
    print("注意: FastAPIサーバーが起動している必要があります")
    print("起動コマンド: python app/main.py または uvicorn app.main:app --reload\n")

    try:
        # 1. ヘルスチェック
        print_section("1. ヘルスチェック")
        response = requests.get(f"{BASE_URL}/health")
        print(f"GET /health")
        print(f"ステータスコード: {response.status_code}")
        print(f"レスポンス: {response.json()}")
        assert response.status_code == 200, "ヘルスチェック失敗"
        print("✅ 成功")

        # 2. デモデータ作成
        print_section("2. デモデータ作成")
        response = requests.post(f"{BASE_URL}/api/v1/seed/demo-data")
        print(f"POST /api/v1/seed/demo-data")
        print(f"ステータスコード: {response.status_code}")
        print(f"レスポンス: {response.json()}")
        assert response.status_code == 201, "デモデータ作成失敗"
        print("✅ 成功")

        # 3. 拠点リスト取得
        print_section("3. 拠点リスト取得")
        response = requests.get(f"{BASE_URL}/api/v1/depots")
        print(f"GET /api/v1/depots")
        print(f"ステータスコード: {response.status_code}")
        data = response.json()
        print(f"取得件数: {data['total']}")
        print(f"最初の拠点: {data['depots'][0]['name']}")
        assert response.status_code == 200, "拠点リスト取得失敗"
        assert data['total'] > 0, "拠点が存在しません"
        print("✅ 成功")

        # 4. 車両リスト取得
        print_section("4. 車両リスト取得")
        response = requests.get(f"{BASE_URL}/api/v1/vehicles")
        print(f"GET /api/v1/vehicles")
        print(f"ステータスコード: {response.status_code}")
        data = response.json()
        print(f"取得件数: {data['total']}")
        if data['total'] > 0:
            print(f"最初の車両: {data['vehicles'][0]['id']} ({data['vehicles'][0]['vehicle_type']})")
        assert response.status_code == 200, "車両リスト取得失敗"
        assert data['total'] > 0, "車両が存在しません"
        print("✅ 成功")

        # 5. 配送先リスト取得
        print_section("5. 配送先リスト取得")
        response = requests.get(f"{BASE_URL}/api/v1/deliveries")
        print(f"GET /api/v1/deliveries")
        print(f"ステータスコード: {response.status_code}")
        data = response.json()
        print(f"取得件数: {data['total']}")
        if data['total'] > 0:
            print(f"最初の配送先: {data['deliveries'][0]['customer_name']}")
        assert response.status_code == 200, "配送先リスト取得失敗"
        assert data['total'] > 0, "配送先が存在しません"
        print("✅ 成功")

        # 6. 配送先フィルタテスト（午前指定）
        print_section("6. 配送先フィルタ（午前指定）")
        response = requests.get(f"{BASE_URL}/api/v1/deliveries?time_window=morning")
        print(f"GET /api/v1/deliveries?time_window=morning")
        print(f"ステータスコード: {response.status_code}")
        data = response.json()
        print(f"午前指定配送先: {data['total']}件")
        assert response.status_code == 200, "配送先フィルタ失敗"
        print("✅ 成功")

        # 7. VRP最適化実行（8配送先、混合時間窓）
        print_section("7. VRP最適化実行（小規模：8配送先）")

        # 混合時間窓の配送先を選択（morning/afternoon/anytime）
        # delivery-001,002,003: morning
        # delivery-004,005: afternoon
        # delivery-007,008: anytime
        # delivery-009: morning
        delivery_ids = [
            "delivery-001", "delivery-002", "delivery-003",
            "delivery-004", "delivery-005",
            "delivery-007", "delivery-008",
            "delivery-009"
        ]

        # 拠点IDと車両IDを取得（3台使用）
        response = requests.get(f"{BASE_URL}/api/v1/depots")
        depot_ids = [d["id"] for d in response.json()["depots"]]

        response = requests.get(f"{BASE_URL}/api/v1/vehicles")
        vehicle_ids = [v["id"] for v in response.json()["vehicles"]]  # 全3台使用

        # 最適化リクエスト
        optimization_request = {
            "depot_ids": depot_ids,
            "vehicle_ids": vehicle_ids,
            "delivery_ids": delivery_ids,
        }

        print(f"POST /api/v1/optimization/optimize")
        print(f"リクエスト:")
        print(f"  拠点: {len(depot_ids)}件")
        print(f"  車両: {len(vehicle_ids)}台")
        print(f"  配送先: {len(delivery_ids)}件（morning: 4, afternoon: 2, anytime: 2）")

        response = requests.post(
            f"{BASE_URL}/api/v1/optimization/optimize",
            json=optimization_request,
            timeout=35  # 30秒 + 5秒マージン
        )

        print(f"ステータスコード: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"\n📊 最適化結果:")
            print(f"  結果ID: {result['id']}")
            print(f"  計算時間: {result['computation_time']}ms")
            print(f"  生成ルート数: {len(result['routes'])}")
            print(f"  総走行距離: {result['total_distance']:.2f} km")
            print(f"  総コスト: ¥{result['total_cost']:,.2f}")
            print(f"  平均積載率: {result['average_utilization_weight']:.2f}%")

            print(f"\n🎯 改善効果:")
            improvement = result['improvement_metrics']
            print(f"  距離削減: {improvement['distance_reduction_km']:.2f} km "
                  f"({improvement['distance_reduction_percent']:.1f}%)")
            print(f"  コスト削減: ¥{improvement['cost_reduction_amount']:,.2f} "
                  f"({improvement['cost_reduction_percent']:.1f}%)")
            print(f"  積載率改善: {improvement['utilization_improvement_percent']:.2f}%")

            assert len(result['routes']) > 0, "ルートが生成されていません"
            print("\n✅ 成功")
        else:
            print(f"❌ 失敗: {response.status_code}")
            print(f"エラー: {response.json()}")
            return False

        # 8. VRP最適化実行（全配送先）
        print_section("8. VRP最適化実行（中規模：全配送先）")

        # 全配送先IDを取得
        response = requests.get(f"{BASE_URL}/api/v1/deliveries")
        all_delivery_ids = [d["id"] for d in response.json()["deliveries"]]

        # 全車両IDを取得
        response = requests.get(f"{BASE_URL}/api/v1/vehicles")
        all_vehicle_ids = [v["id"] for v in response.json()["vehicles"]]

        optimization_request = {
            "depot_ids": depot_ids,
            "vehicle_ids": all_vehicle_ids,
            "delivery_ids": all_delivery_ids,
        }

        print(f"POST /api/v1/optimization/optimize")
        print(f"リクエスト:")
        print(f"  拠点: {len(depot_ids)}件")
        print(f"  車両: {len(all_vehicle_ids)}台")
        print(f"  配送先: {len(all_delivery_ids)}件")

        response = requests.post(
            f"{BASE_URL}/api/v1/optimization/optimize",
            json=optimization_request,
            timeout=35
        )

        print(f"ステータスコード: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"\n📊 最適化結果:")
            print(f"  結果ID: {result['id']}")
            print(f"  計算時間: {result['computation_time']}ms")
            print(f"  生成ルート数: {len(result['routes'])}")
            print(f"  総走行距離: {result['total_distance']:.2f} km")
            print(f"  総コスト: ¥{result['total_cost']:,.2f}")
            print(f"  平均積載率: {result['average_utilization_weight']:.2f}%")
            print(f"  未割当配送先: {len(result['unassigned_deliveries'])}件")

            print(f"\n🎯 改善効果:")
            improvement = result['improvement_metrics']
            print(f"  距離削減: {improvement['distance_reduction_km']:.2f} km "
                  f"({improvement['distance_reduction_percent']:.1f}%)")
            print(f"  コスト削減: ¥{improvement['cost_reduction_amount']:,.2f} "
                  f"({improvement['cost_reduction_percent']:.1f}%)")
            print(f"  積載率改善: {improvement['utilization_improvement_percent']:.2f}%")

            print(f"\n🚛 ルート詳細:")
            for i, route in enumerate(result['routes'], 1):
                print(f"  ルート {i}: {len(route['stops'])}箇所, "
                      f"{route['total_distance']:.2f}km, "
                      f"積載率 {route['utilization_weight']:.1f}%")

            assert len(result['routes']) > 0, "ルートが生成されていません"
            print("\n✅ 成功")
        else:
            print(f"❌ 失敗: {response.status_code}")
            print(f"エラー: {response.json()}")
            return False

        # 全テスト成功
        print("\n" + "=" * 70)
        print("✅ すべてのAPIテストが成功しました！")
        print("=" * 70)
        return True

    except requests.exceptions.ConnectionError:
        print("\n❌ エラー: FastAPIサーバーに接続できません")
        print("サーバーを起動してください: python app/main.py")
        return False

    except AssertionError as e:
        print(f"\n❌ アサーションエラー: {e}")
        return False

    except Exception as e:
        print(f"\n❌ 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)
