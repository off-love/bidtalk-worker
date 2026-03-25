import os
import sys

sys.path.insert(0, os.path.abspath("."))

from concurrent.futures import ThreadPoolExecutor
from src.api.bid_client import fetch_bid_notices
from src.api.prebid_client import fetch_prebid_notices
from src.core.models import BidType

import logging
logging.basicConfig(level=logging.DEBUG)

def fetch_bids():
    try:
        res = fetch_bid_notices(BidType.SERVICE, "용역", buffer_hours=24, max_results=50)
        print(f"[BID] Fetched {len(res)} notices")
        return res
    except Exception as e:
        print(f"[BID] Error: {e}")
        return []

def fetch_prebids():
    try:
        res = fetch_prebid_notices(BidType.SERVICE, "용역", buffer_hours=24, max_results=50)
        print(f"[PREBID] Fetched {len(res)} notices")
        return res
    except Exception as e:
        print(f"[PREBID] Error: {e}")
        return []

def main():
    print("Testing concurrent fetching...")
    with ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(fetch_bids)
        f2 = executor.submit(fetch_prebids)
        
        bids = f1.result()
        prebids = f2.result()
        
    print(f"Final Count - Bid: {len(bids)}, Prebid: {len(prebids)}")

if __name__ == "__main__":
    main()
