import os
import sys

from src.api.bid_client import fetch_bid_notices
from src.core.models import BidType

# we need to set the api key explicitly or use the one from env if available
# wait, github actions has the key, let's see if the local machine has the env var.
try:
    notices = fetch_bid_notices(BidType.SERVICE, "측량", 60 * 24 * 7) # last 7 days
    print(f"측량 service: {len(notices)}")
except Exception as e:
    print(f"error: {e}")

try:
    notices = fetch_bid_notices(BidType.SERVICE, "용역", 60 * 24 * 7) # last 7 days
    print(f"용역 service: {len(notices)}")
except Exception as e:
    print(f"error: {e}")
