import os
import sys

# Add src to python path for testing
sys.path.insert(0, os.path.abspath("."))

from src.api.prebid_client import fetch_prebid_notices
from src.core.models import BidType

import logging
logging.basicConfig(level=logging.DEBUG)

def main():
    print("Testing Prebid API with keyword '용역' under SERVICE bid type...")
    # Trying SERVICE bid type, which matches '용역'
    try:
        notices = fetch_prebid_notices(BidType.SERVICE, "용역", buffer_hours=240, max_results=10)
        print(f"Found {len(notices)} notices.")
        for n in notices:
            print(f"- {n.prcure_nm} ({n.prcure_no})")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
