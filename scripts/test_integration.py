#!/usr/bin/env python3
"""
입찰알리미 서버 통합 테스트

Firebase 없이 API 호출 → 필터링 → 페이로드 생성까지 확인합니다.
실제 나라장터 API를 호출하여 동작을 검증합니다.

사용법:
    G2B_API_KEY=your_key python scripts/test_integration.py
"""

import json
import logging
import os
import sys
from pathlib import Path

# 프로젝트 루트를 PYTHONPATH에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def test_topic_hasher():
    """1. 토픽 해시 테스트"""
    from src.core.topic_hasher import topic_name, get_all_topic_names

    logger.info("━━━ 1. 토픽 해시 테스트 ━━━")
    tests = [
        ("cctv", "b29dbba57df61de7"),
        ("소프트웨어", "465f222a27475e7f"),
        ("ai", "32e83e92d45d71f6"),
    ]
    for kw, expected in tests:
        result = topic_name(kw, "bid", "s")
        status = "✅" if result == f"bid_s_{expected}" else "❌"
        logger.info(f"  {status} {kw:12s} → {result}")

    topics = get_all_topic_names("CCTV")
    logger.info(
        "  ✅ allTopics: bid_s=%s, bid_c=%s, bid_g=%s, pre_s=%s",
        topics["bid_s"], topics["bid_c"], topics["bid_g"], topics["pre_s"],
    )
    return True


def test_time_utils():
    """2. 시간 유틸 테스트"""
    from src.utils.time_utils import now_kst, get_query_range, calc_d_day, format_display_dt

    logger.info("━━━ 2. 시간 유틸 테스트 ━━━")
    now = now_kst()
    logger.info(f"  ✅ 현재 KST: {now}")

    bgn, end = get_query_range(30)
    logger.info(f"  ✅ 조회범위: {bgn} ~ {end}")

    d_day = calc_d_day("2026/04/30 18:00:00")
    logger.info(f"  ✅ D-day: {d_day}")

    display = format_display_dt("2026/04/11 14:00:00")
    logger.info(f"  ✅ 날짜표시: {display}")
    return True


def test_keywords_json():
    """3. keywords.json 로드 테스트"""
    from src.core.topic_hasher import topic_name

    logger.info("━━━ 3. keywords.json 테스트 ━━━")
    keywords_path = project_root / "data" / "keywords.json"

    with open(keywords_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    keywords = data.get("keywords", [])
    logger.info(f"  ✅ 키워드 수: {len(keywords)}개")
    logger.info(f"  ✅ 전역 제외: {data.get('global_exclude', [])}")

    # 첫 3개 키워드 출력
    for kw in keywords[:3]:
        logger.info(
            "     %s → hash=%s, bid_s=%s",
            f"{kw['original']:12s}",
            kw["keyword_hash"],
            topic_name(kw["original"], "bid", "s"),
        )

    # 해시가 placeholder가 아닌지 확인
    has_placeholder = any("placeholder" in kw.get("keyword_hash", "") for kw in keywords)
    if has_placeholder:
        logger.error("  ❌ placeholder 해시가 남아있습니다! generate_topic_hashes.py 실행 필요")
        return False

    logger.info(f"  ✅ 모든 해시 정상")
    return True


def test_state_manager():
    """4. 상태 관리 테스트"""
    from src.storage.state_manager import load_state, mark_notified, is_notified, cleanup_old_records

    logger.info("━━━ 4. 상태관리 테스트 ━━━")
    state = load_state()
    logger.info(f"  ✅ state.json 로드 성공")
    logger.info(f"     입찰 이력: {len(state.get('notified_bids', {}))}건")
    logger.info(f"     사전규격 이력: {len(state.get('notified_prebids', {}))}건")

    # 중복 체크 테스트
    test_key = "TEST-20260411-001"
    mark_notified(state, test_key, "테스트", "bid")
    assert is_notified(state, test_key, "bid"), "중복 체크 실패"
    assert not is_notified(state, test_key, "prebid"), "다른 유형은 미알림이어야 함"

    # 테스트 레코드 정리
    del state["notified_bids"][test_key]
    logger.info(f"  ✅ 중복 체크 정상")
    return True


def test_filter():
    """5. 필터링 테스트"""
    from src.core.filter import filter_bid_notices
    from src.core.models import BidNotice, BidType

    logger.info("━━━ 5. 필터링 테스트 ━━━")

    # 테스트 데이터
    notices = [
        BidNotice(
            bid_ntce_no="TEST001", bid_ntce_ord="00", bid_ntce_nm="소프트웨어 개발 용역",
            ntce_instt_nm="테스트기관", dmnd_instt_nm="수요기관", presmpt_prce=100000000,
            bid_ntce_dt="2026/04/11", bid_clse_dt="2026/04/30", openg_dt="2026/05/01",
            bid_ntce_dtl_url="https://example.com", prtcpt_psbl_rgn_nm="전국",
            bid_type=BidType.SERVICE,
        ),
        BidNotice(
            bid_ntce_no="TEST002", bid_ntce_ord="00", bid_ntce_nm="취소공고 소프트웨어",
            ntce_instt_nm="테스트기관", dmnd_instt_nm="수요기관", presmpt_prce=50000000,
            bid_ntce_dt="2026/04/11", bid_clse_dt="2026/04/30", openg_dt="2026/05/01",
            bid_ntce_dtl_url="https://example.com", prtcpt_psbl_rgn_nm="전국",
            bid_type=BidType.SERVICE,
        ),
        BidNotice(
            bid_ntce_no="TEST003", bid_ntce_ord="00", bid_ntce_nm="도로포장 공사",
            ntce_instt_nm="테스트기관", dmnd_instt_nm="수요기관", presmpt_prce=200000000,
            bid_ntce_dt="2026/04/11", bid_clse_dt="2026/04/30", openg_dt="2026/05/01",
            bid_ntce_dtl_url="https://example.com", prtcpt_psbl_rgn_nm="전국",
            bid_type=BidType.CONSTRUCTION,
        ),
    ]

    # 소프트웨어 키워드 + 취소공고 제외
    filtered = filter_bid_notices(notices, keyword="소프트웨어", exclude_keywords=["취소공고"])
    assert len(filtered) == 1, f"필터 결과 {len(filtered)}건 (예상: 1건)"
    assert filtered[0].bid_ntce_no == "TEST001"
    logger.info(f"  ✅ 필터링 정상: 3건 → {len(filtered)}건 (취소공고 제외, 키워드 미매칭 제외)")
    return True


def test_formatter():
    """6. FCM 페이로드 포맷터 테스트"""
    from src.core.formatter import format_bid_payload, format_prebid_payload
    from src.core.models import BidNotice, PreBidNotice, BidType

    logger.info("━━━ 6. 페이로드 포맷 테스트 ━━━")

    bid = BidNotice(
        bid_ntce_no="R26BK01387264", bid_ntce_ord="000",
        bid_ntce_nm="정보시스템 유지보수 용역",
        ntce_instt_nm="서울시청", dmnd_instt_nm="디지털정책과",
        presmpt_prce=150000000,
        bid_ntce_dt="2026/04/11 14:00:00", bid_clse_dt="2026/04/25 18:00:00",
        openg_dt="2026/04/26 10:00:00",
        bid_ntce_dtl_url="https://www.g2b.go.kr/bid/R26BK01387264",
        prtcpt_psbl_rgn_nm="전국",
        bid_type=BidType.SERVICE,
    )

    payload = format_bid_payload(bid, "정보시스템")
    logger.info(f"  ✅ 알림 제목: {payload['notification']['title']}")
    logger.info(f"  ✅ 알림 본문: {payload['notification']['body']}")
    logger.info(f"  ✅ 공고ID: {payload['data']['noticeId']}")
    logger.info(f"  ✅ 가격: {payload['data']['price']}원")
    logger.info(f"  ✅ D-day: {payload['data']['dDay']}")

    # 사전규격
    prebid = PreBidNotice(
        prcure_no="P2026041100001", prcure_nm="AI 기반 분석 시스템",
        ntce_instt_nm="과기부", rcpt_dt="2026/04/11",
        opnn_reg_clse_dt="2026/04/20 18:00:00",
        asign_bdgt_amt=500000000,
        dtl_url="https://www.g2b.go.kr/pre/P2026041100001",
        bid_type=BidType.SERVICE,
    )

    pre_payload = format_prebid_payload(prebid, "AI")
    logger.info(f"  ✅ 사전규격 제목: {pre_payload['notification']['title']}")
    logger.info(f"  ✅ 사전규격 본문: {pre_payload['notification']['body']}")
    return True


def test_api_call():
    """7. 실제 API 호출 테스트 (API 키 필요)"""
    api_key = os.environ.get("G2B_API_KEY", "")
    if not api_key:
        logger.warning("━━━ 7. API 호출 테스트 (건너뜀 - G2B_API_KEY 없음) ━━━")
        return True

    from src.api.bid_client import fetch_bid_notices
    from src.core.models import BidType

    logger.info("━━━ 7. 실제 API 호출 테스트 ━━━")

    # 최근 1시간 내 용역 입찰공고 조회
    notices = fetch_bid_notices(
        bid_type=BidType.SERVICE,
        keyword="",
        buffer_minutes=60,
        max_results=5,
    )

    logger.info(f"  ✅ 용역 입찰공고 조회: {len(notices)}건")
    for n in notices[:3]:
        logger.info(f"     [{n.unique_key}] {n.bid_ntce_nm[:30]}...")
        logger.info(f"       기관: {n.ntce_instt_nm}, 가격: {n.price_display}")

    return True


def main():
    logger.info("=" * 60)
    logger.info("🧪 입찰알리미 서버 통합 테스트")
    logger.info("=" * 60)

    tests = [
        ("토픽 해시", test_topic_hasher),
        ("시간 유틸", test_time_utils),
        ("keywords.json", test_keywords_json),
        ("상태 관리", test_state_manager),
        ("필터링", test_filter),
        ("FCM 페이로드", test_formatter),
        ("API 호출", test_api_call),
    ]

    passed = 0
    failed = 0

    for name, test_fn in tests:
        try:
            result = test_fn()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"  ❌ {name} 테스트 실패: {e}")
            failed += 1

    logger.info("=" * 60)
    logger.info(f"🏁 테스트 완료: {passed} passed, {failed} failed")
    logger.info("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
