#!/usr/bin/env python3
"""
keywords.json의 keyword_hash를 실제 SHA256 해시로 갱신합니다.

사용법:
    python scripts/generate_topic_hashes.py
"""

import json
import sys
from pathlib import Path

# 프로젝트 루트를 PYTHONPATH에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.topic_hasher import keyword_hash, get_all_topic_names


def main():
    keywords_path = project_root / "data" / "keywords.json"

    with open(keywords_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated = 0
    for kw in data["keywords"]:
        new_hash = keyword_hash(kw["original"])
        if kw.get("keyword_hash") != new_hash:
            kw["keyword_hash"] = new_hash
            updated += 1

            # 토픽 이름 예시 출력
            topics = get_all_topic_names(kw["original"])
            print(f"  ✓ {kw['original']:12s} → hash={new_hash}")
            print(f"    bid: {topics['bid_s']}, {topics['bid_c']}, {topics['bid_g']}")
            print(f"    pre: {topics['pre_s']}, {topics['pre_c']}, {topics['pre_g']}")

    with open(keywords_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {updated}개 키워드 해시 업데이트 완료")


if __name__ == "__main__":
    main()
