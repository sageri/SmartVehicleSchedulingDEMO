"""
データベース初期化スクリプト

すべてのテーブルを作成します。
"""

import sys
from pathlib import Path

# プロジェクトルートを sys.path に追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import init_db


if __name__ == "__main__":
    print("🚀 データベース初期化を開始します...")
    init_db()
    print("✅ 完了しました！")
