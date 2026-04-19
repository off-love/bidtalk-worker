import os
import sys

# add current directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.api.bid_client import fetch_bid_notices
from src.api.prebid_client import fetch_prebid_notices
from src.core.models import BidType

buffer_minutes = 60 * 24 * 7  # past 7 days
test_keyword = "건축"

def run_test():
    bid_types = [
        (BidType.SERVICE, "용역 (SERVICE)"),
        (BidType.CONSTRUCTION, "공사 (CONSTRUCTION)"),
        (BidType.GOODS, "물품 (GOODS)")
    ]
    
    print("=== [테스트 1] 입찰공고(bid) API 연동 ===")
    for bt, name in bid_types:
        try:
            notices = fetch_bid_notices(bt, test_keyword, buffer_minutes, max_results=10)
            print(f"✅ {name}: 성공적으로 연동되었습니다. (예시 '{test_keyword}' 검색: {len(notices)}건 반환됨)")
        except Exception as e:
            print(f"❌ {name}: 호출 실패 - {e}")

    print("\n=== [테스트 2] 사전규격(prebid) API 연동 ===")
    for bt, name in bid_types:
        try:
            notices = fetch_prebid_notices(bt, test_keyword, buffer_minutes, max_results=10)
            print(f"✅ {name}: 성공적으로 연동되었습니다. (예시 '{test_keyword}' 검색: {len(notices)}건 반환됨)")
        except Exception as e:
            print(f"❌ {name}: 호출 실패 - {e}")

if __name__ == "__main__":
    run_test()
