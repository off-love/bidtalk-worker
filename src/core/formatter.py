"""
FCM 메시지 페이로드 포맷터

입찰공고/사전규격 데이터를 FCM 푸시 알림 페이로드로 변환합니다.
"""

from __future__ import annotations

from src.core.models import BidNotice, PreBidNotice
from src.utils.time_utils import calc_d_day, format_display_dt, now_iso


def format_bid_payload(notice: BidNotice, keyword: str) -> dict:
    """입찰공고를 FCM 페이로드로 변환

    Args:
        notice: 입찰공고 데이터
        keyword: 매칭된 키워드

    Returns:
        FCM data 페이로드 (dict)
    """
    d_day = calc_d_day(notice.bid_clse_dt)

    return {
        "notification": {
            "title": "🔔 새 입찰공고",
            "body": f"[{keyword}] {notice.bid_ntce_nm}",
        },
        "data": {
            "noticeId": notice.unique_key,
            "title": notice.bid_ntce_nm,
            "agency": notice.ntce_instt_nm,
            "demandAgency": notice.dmnd_instt_nm,
            "price": str(notice.presmpt_prce),
            "closingDate": notice.bid_clse_dt,
            "noticeDate": notice.bid_ntce_dt,
            "detailUrl": notice.bid_ntce_dtl_url,
            "bidType": notice.bid_type.value,
            "keyword": keyword,
            "type": "bid",
            "region": notice.prtcpt_psbl_rgn_nm,
            "contractMethod": notice.cntrct_methd_nm,
            "dDay": d_day,
            "timestamp": now_iso(),
        },
    }


def format_prebid_payload(notice: PreBidNotice, keyword: str) -> dict:
    """사전규격을 FCM 페이로드로 변환

    Args:
        notice: 사전규격 데이터
        keyword: 매칭된 키워드

    Returns:
        FCM data 페이로드 (dict)
    """
    d_day = calc_d_day(notice.opnn_reg_clse_dt)

    return {
        "notification": {
            "title": "📋 새 사전규격",
            "body": f"[{keyword}] {notice.prcure_nm}",
        },
        "data": {
            "noticeId": notice.unique_key,
            "title": notice.prcure_nm,
            "agency": notice.ntce_instt_nm,
            "demandAgency": "",
            "price": str(notice.asign_bdgt_amt),
            "closingDate": notice.opnn_reg_clse_dt,
            "noticeDate": notice.rcpt_dt,
            "detailUrl": notice.dtl_url,
            "bidType": notice.bid_type.value,
            "keyword": keyword,
            "type": "prebid",
            "region": "",
            "contractMethod": "",
            "dDay": d_day,
            "timestamp": now_iso(),
        },
    }
