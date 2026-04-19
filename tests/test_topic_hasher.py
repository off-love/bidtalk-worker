"""
토픽 해시 일관성 테스트

iOS(Swift)와 Python 사이의 해시가 동일한지 검증합니다.
이 테스트는 최우선 검증 항목입니다.

사용법:
    python -m pytest tests/test_topic_hasher.py -v
"""

import sys
from pathlib import Path

# 프로젝트 루트를 PYTHONPATH에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.topic_hasher import get_all_topic_names, topic_name


# ─── 해시 일관성 테스트 ──────────────────────────────────────────

def test_basic_keyword():
    """기본 한글 키워드 해시"""
    result = topic_name("CCTV", "bid")
    assert result.startswith("bid_"), f"접두사 오류: {result}"
    assert len(result) == 4 + 16, f"길이 오류: {len(result)} (expected 20)"
    # CCTV는 대소문자 무관하게 동일해야 함
    assert topic_name("CCTV", "bid") == topic_name("cctv", "bid")


def test_korean_keyword():
    """한글 키워드 해시"""
    result = topic_name("소프트웨어", "bid")
    assert result.startswith("bid_")
    assert len(result) == 20


def test_prebid_prefix():
    """사전규격 접두사"""
    bid = topic_name("CCTV", "bid")
    pre = topic_name("CCTV", "pre")
    assert bid.startswith("bid_")
    assert pre.startswith("pre_")
    # 해시 부분은 동일해야 함
    assert bid[4:] == pre[4:]


def test_whitespace_normalization():
    """앞뒤 공백 제거 후 동일 해시"""
    assert topic_name("CCTV", "bid") == topic_name("  CCTV  ", "bid")
    assert topic_name("소프트웨어", "bid") == topic_name(" 소프트웨어 ", "bid")


def test_case_normalization():
    """대소문자 무관 동일 해시"""
    assert topic_name("AI", "bid") == topic_name("ai", "bid")
    assert topic_name("Cctv", "bid") == topic_name("cctv", "bid")


def test_get_all_topic_names():
    """bid + pre 동시 조회"""
    result = get_all_topic_names("CCTV")
    assert "bid_topic" in result
    assert "pre_topic" in result
    assert result["bid_topic"].startswith("bid_")
    assert result["pre_topic"].startswith("pre_")


def test_fcm_topic_safe_characters():
    """FCM Topic 이름은 [a-zA-Z0-9-_.~%] 만 허용"""
    import re
    fcm_pattern = re.compile(r'^[a-zA-Z0-9\-_.~%]+$')

    test_keywords = [
        "CCTV", "소프트웨어", "AI", "클라우드", "지적측량",
        "출입통제", "네트워크", "데이터베이스", "사무용품",
    ]

    for kw in test_keywords:
        bid = topic_name(kw, "bid")
        pre = topic_name(kw, "pre")
        assert fcm_pattern.match(bid), f"FCM 규칙 위반: {bid} (keyword: {kw})"
        assert fcm_pattern.match(pre), f"FCM 규칙 위반: {pre} (keyword: {kw})"


def test_known_hashes():
    """알려진 해시값 (iOS 구현 시 이 값들과 대조할 것)

    ⚠️ 이 테스트값들은 iOS Swift CryptoKit 구현에서도
    동일한 결과가 나와야 합니다!
    """
    known = {
        "cctv": "b29dbba57df61de7",       # "CCTV".lowercased()
        "소프트웨어": "465f222a27475e7f",
        "ai": "32e83e92d45d71f6",          # "AI".lowercased()
        "측량": "5f66b02e337d9504",
    }

    for keyword, expected_hash in known.items():
        result = topic_name(keyword, "bid")
        assert result == f"bid_{expected_hash}", (
            f"해시 불일치! keyword={keyword}, "
            f"expected=bid_{expected_hash}, got={result}"
        )


# ─── 메인 실행 ──────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        test_basic_keyword,
        test_korean_keyword,
        test_prebid_prefix,
        test_whitespace_normalization,
        test_case_normalization,
        test_get_all_topic_names,
        test_fcm_topic_safe_characters,
        test_known_hashes,
    ]

    print("🧪 토픽 해시 일관성 테스트")
    print("=" * 50)

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            print(f"  ✅ {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  ❌ {test.__name__}: {e}")
            failed += 1

    print("=" * 50)
    print(f"결과: {passed} passed, {failed} failed")

    if failed > 0:
        sys.exit(1)
