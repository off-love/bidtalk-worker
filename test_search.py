import os
import sys

sys.path.insert(0, os.path.abspath("."))

from src.update_handler import handle_search_command
from src.telegram_bot import send_message

def dummy_send_message(text, chat_id=None, parse_mode="HTML", disable_web_page_preview=True, reply_markup=None):
    print(f"SEND_MESSAGE: {text[:200]}")
    return True

import src.update_handler
src.update_handler.send_message = dummy_send_message

import src.telegram_bot
src.update_handler.send_bid_notifications = lambda msgs: print(f"SEND_NOTIFS: {len(msgs)} messages")

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    print("Testing handle_search_command('123', ['용역'])")
    handle_search_command("123", ["용역"])
