import os
import sys

# Load .env file manually
# Load .env file manually
def load_env():
    os.environ["TELEGRAM_BOT_TOKEN"] = "8707382505:AAEDW4THAdAqj4ArquoPob59B6BhIzrA94Y"
    os.environ["TELEGRAM_CHAT_ID"] = "912444204"
    os.environ["G2B_API_KEY"] = "252f3acd8f800d9b8000b7a1f522d1527d6d1273c5eb33532f6d1edfd3510029"

load_env()

# Append current directory to sys.path
sys.path.insert(0, os.path.abspath("."))

from src.api.bid_client import fetch_bid_notices
from src.core.formatter import format_bid_notice
from src.telegram_bot import send_message
from src.core.models import BidType

def test_integration():
    print("=== API Integration Test ===")
    print("1. Fetching recent bid notices from G2B API (Keyword: '청소')")
    
    try:
        notices = fetch_bid_notices(
            bid_type=BidType.SERVICE,
            keyword="청소",
            buffer_hours=24,
            max_results=3
        )
        print(f"-> Fetched {len(notices)} notices.")
    except Exception as e:
        print(f"-> [FAIL] API fetch failed: {e}")
        return

    if not notices:
        print("-> No notices found. Let's try a different keyword ('용역').")
        try:
            notices = fetch_bid_notices(
                bid_type=BidType.SERVICE,
                keyword="용역",
                buffer_hours=48,
                max_results=3
            )
            print(f"-> Fetched {len(notices)} notices.")
        except Exception as e:
            print(f"-> [FAIL] API fetch failed: {e}")
            return

    if not notices:
        print("-> [WARN] No notices found in API. Sending a generic test message to Telegram.")
        msg = "🚀 <b>나라장터 API + 텔레그램 연동 테스트</b>\n\n현재 검색되는 최근 공고가 없습니다. 연동은 정상입니다."
    else:
        print("2. Formatting the first notice")
        notice = notices[0]
        # Profile name is '테스트'
        msg = format_bid_notice(notice, profile_name="테스트", matched_keyword="테스트")
        msg = f"🚀 <b>나라장터 API + 텔레그램 연동 테스트</b>\n(아래는 실제 공고 샘플입니다)\n\n" + msg
        print(f"-> Formatted message:\n{msg}")

    print("3. Sending message to Telegram")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not chat_id or not bot_token:
        print("-> [FAIL] Missing TELEGRAM_CHAT_ID or TELEGRAM_BOT_TOKEN in .env")
        return
        
    try:
        success = send_message(msg, chat_id=chat_id)
        if success:
            print("-> [SUCCESS] Telegram message sent successfully!")
        else:
            print("-> [FAIL] Telegram message sending returned False.")
    except Exception as e:
        print(f"-> [FAIL] Telegram sending failed with exception: {e}")

if __name__ == "__main__":
    test_integration()
