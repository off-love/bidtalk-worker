"""
2단계 필터링 엔진

1단계 (API 레벨): bidNtceNm → bid_client.py에서 처리
2단계 (코드 레벨): 제외 키워드, OR 키워드 재확인 → 이 모듈에서 처리

기존 나라장터_입찰공고 프로젝트에서 검증된 코드 재활용 (간소화).
"""

from __future__ import annotations

import logging
from typing import Sequence

from src.core.models import BidNotice, PreBidNotice

logger = logging.getLogger(__name__)


def _match_exclude_keywords(name: str, exclude_keywords: list[str]) -> bool:
    """제외 키워드: 하나라도 포함되면 True (= 제외 대상)"""
    if not exclude_keywords:
        return False
    name_lower = name.lower()
    return any(kw.lower() in name_lower for kw in exclude_keywords)


def _match_keyword(name: str, keyword: str) -> bool:
    """키워드가 공고명에 포함되는지 확인 (API 필터 누락 대비 방어 로직)"""
    if not keyword:
        return True
    return keyword.lower() in name.lower()


def filter_bid_notices(
    notices: Sequence[BidNotice],
    keyword: str = "",
    exclude_keywords: list[str] | None = None,
) -> list[BidNotice]:
    """입찰공고 목록에 코드 레벨 필터링을 적용합니다.

    필터 순서:
    1. 제외 키워드 → 제거
    2. OR 키워드 재확인 → API 필터 누락 대비

    Args:
        notices: API에서 조회한 공고 목록
        keyword: 매칭 키워드
        exclude_keywords: 제외 키워드 목록

    Returns:
        필터 통과한 BidNotice 리스트
    """
    if exclude_keywords is None:
        exclude_keywords = []

    result: list[BidNotice] = []

    for notice in notices:
        bid_name = notice.bid_ntce_nm

        # 1. 제외 키워드 체크
        if _match_exclude_keywords(bid_name, exclude_keywords):
            logger.debug("제외됨 (키워드): %s", bid_name)
            continue

        # 2. 키워드 재확인 (API 필터 누락 대비)
        if not _match_keyword(bid_name, keyword):
            logger.debug("제외됨 (OR): %s", bid_name)
            continue

        result.append(notice)

    logger.info(
        "입찰 필터링: %d건 → %d건 (키워드: %s)",
        len(notices), len(result), keyword or "전체",
    )
    return result


def filter_prebid_notices(
    notices: Sequence[PreBidNotice],
    keyword: str = "",
    exclude_keywords: list[str] | None = None,
) -> list[PreBidNotice]:
    """사전규격 목록에 코드 레벨 필터링을 적용합니다."""
    if exclude_keywords is None:
        exclude_keywords = []

    result: list[PreBidNotice] = []

    for notice in notices:
        name = notice.prcure_nm

        if _match_exclude_keywords(name, exclude_keywords):
            logger.debug("제외됨 (키워드): %s", name)
            continue

        if not _match_keyword(name, keyword):
            logger.debug("제외됨 (OR): %s", name)
            continue

        result.append(notice)

    logger.info(
        "사전규격 필터링: %d건 → %d건 (키워드: %s)",
        len(notices), len(result), keyword or "전체",
    )
    return result
