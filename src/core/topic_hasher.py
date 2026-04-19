"""
키워드 → FCM Topic 해시 변환

iOS(Swift)와 Python 양쪽에서 동일한 해시를 생성해야 합니다.
정규화 순서: strip() → lower() → SHA256 → hexdigest[:16]

토픽 이름 형식:
  {noti_type}_{bid_category}_{hash}
  - noti_type: "bid" (입찰공고) 또는 "pre" (사전규격)
  - bid_category: "s" (용역), "c" (공사), "g" (물품)
  - hash: 키워드의 SHA256 hex[:16]

예시: topic_name("cctv", "bid", "s") → "bid_s_b29dbba57df61de7"
"""

from __future__ import annotations

import hashlib
import unicodedata


def keyword_hash(keyword: str) -> str:
    """키워드를 SHA256 해시 16자로 변환

    Args:
        keyword: 원본 키워드 (예: "CCTV", "소프트웨어")

    Returns:
        hex 해시 문자열 (16자)
    """
    # Unicode NFD/NFC 불일치를 방지하기 위해 NFC로 강제 정규화
    normalized = unicodedata.normalize('NFC', keyword.strip().lower())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def topic_name(keyword: str, noti_type: str = "bid", bid_category: str = "s") -> str:
    """키워드를 FCM Topic 이름으로 변환

    FCM Topic 이름 규칙: [a-zA-Z0-9-_.~%]{1,900}
    한글 키워드를 SHA256 해시로 변환합니다.

    Args:
        keyword: 원본 키워드 (예: "CCTV", "소프트웨어")
        noti_type: "bid" (입찰공고) 또는 "pre" (사전규격)
        bid_category: "s" (용역/service), "c" (공사/construction), "g" (물품/goods)

    Returns:
        FCM Topic 이름 (예: "bid_s_b29dbba57df61de7")
    """
    prefix = f"{noti_type}_{bid_category}_"
    hex_hash = keyword_hash(keyword)
    return f"{prefix}{hex_hash}"


def get_all_topic_names(keyword: str) -> dict[str, str]:
    """키워드의 모든 업무구분별 토픽 이름을 반환 (6개)

    Args:
        keyword: 원본 키워드

    Returns:
        {
            "bid_s": "bid_s_...", "bid_c": "bid_c_...", "bid_g": "bid_g_...",
            "pre_s": "pre_s_...", "pre_c": "pre_c_...", "pre_g": "pre_g_...",
        }
    """
    result = {}
    for noti_type in ("bid", "pre"):
        for cat in ("s", "c", "g"):
            key = f"{noti_type}_{cat}"
            result[key] = topic_name(keyword, noti_type, cat)
    return result
