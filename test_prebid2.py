import os
import sys

sys.path.insert(0, os.path.abspath("."))

from src.api.prebid_client import fetch_prebid_notices
from src.core.filter import filter_prebid_notices
from src.core.models import BidType, AlertProfile, KeywordConfig
import logging

logging.basicConfig(level=logging.DEBUG)

def main():
    profile = AlertProfile(
        name="Test Profile",
        bid_types=[BidType.SERVICE],
        keywords=KeywordConfig(or_keywords=["용역"], and_keywords=[], exclude=[]),
        include_prebid=True,
    )
    
    raw = fetch_prebid_notices(BidType.SERVICE, "용역", buffer_hours=24, max_results=50)
    print(f"Raw notices count: {len(raw)}")
    
    filtered = filter_prebid_notices(raw, profile)
    print(f"Filtered notices count: {len(filtered)}")

if __name__ == "__main__":
    main()
