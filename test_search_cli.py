
import os
import sys
import logging
from typing import Any

# 프로젝트 루트를 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.api.bid_client import fetch_bid_notices_multi_keywords
from src.api.prebid_client import fetch_prebid_notices
from src.core.filter import filter_bid_notices, filter_prebid_notices
from src.core.formatter import format_bid_notice, format_prebid_notice
from src.storage.profile_manager import load_profiles

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def run_test_search(keyword: str):
    """지정된 키워드로 입찰공고 및 사전규격을 검색하여 터미널에 출력합니다."""
    print(f"\n🔎 '{keyword}' 키워드로 최근 24시간 내 공시를 검색합니다...\n")

    profiles, settings_obj = load_profiles()
    if not profiles:
        print("❌ 활성화된 프로필이 없습니다. config/profiles.yaml을 확인하십시오.")
        return

    profile = profiles[0]
    buffer_hours = 24  # 테스트를 위해 24시간 범위로 고정
    
    bid_results = []
    prebid_results = []

    # 1. 입찰공고 검색
    for bid_type in profile.bid_types:
        print(f"📡 {bid_type.display_name} 입찰공고 조회 중...")
        raw_bids = fetch_bid_notices_multi_keywords(
            bid_type=bid_type,
            keywords=[keyword],
            buffer_hours=buffer_hours
        )
        filtered_bids = filter_bid_notices(raw_bids, profile)
        bid_results.extend(filtered_bids)

    # 2. 사전규격 검색
    if profile.include_prebid:
        seen_prebid_keys = set()
        for bid_type in profile.bid_types:
            print(f"📡 {bid_type.display_name} 사전규격 조회 중...")
            raw_prebids = fetch_prebid_notices(
                bid_type=bid_type,
                keyword=keyword,
                buffer_hours=buffer_hours
            )
            filtered_prebids = filter_prebid_notices(raw_prebids, profile)
            for prebid in filtered_prebids:
                if prebid.unique_key not in seen_prebid_keys:
                    seen_prebid_keys.add(prebid.unique_key)
                    prebid_results.append(prebid)

    print("\n" + "="*50)
    print(f"✅ 검색 결과 요약: 입찰공고 {len(bid_results)}건, 사전규격 {len(prebid_results)}건")
    print("="*50 + "\n")

    if bid_results:
        print("🔔 [입찰공고 리스트]")
        for notice in bid_results:
            print(f"- [{notice.bid_type.display_name}] {notice.bid_ntce_nm} ({notice.ntce_instt_nm})")
    
    if prebid_results:
        print("\n📢 [사전규격 리스트]")
        for prebid in prebid_results:
            print(f"- [{prebid.bid_type.display_name}] {prebid.prcure_nm} ({prebid.ntce_instt_nm})")

    if not bid_results and not prebid_results:
        print("🤷‍♂️ 검색 결과가 없습니다.")

if __name__ == "__main__":
    # 실행 시 인자로 키워드를 받을 수 있음 (기본값: 청소)
    search_keyword = sys.argv[1] if len(sys.argv) > 1 else "청소"
    
    # 필수 환경변수 체크
    if not os.environ.get("G2B_API_KEY"):
        print("⚠️  G2B_API_KEY 환경변수가 설정되지 않았습니다.")
        print("   실행 전 'export G2B_API_KEY=발급받은키'를 입력해 주세요.")
        sys.exit(1)

    try:
        run_test_search(search_keyword)
    except Exception as e:
        print(f"❌ 검색 중 오류 발생: {e}")
