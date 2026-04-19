"""
데이터 모델 — 입찰공고, 사전규격, 키워드 설정

기존 나라장터_입찰공고/사전규격 프로젝트에서 재활용.
텔레그램 관련 모델(BroadcastResult 등)은 제거하고,
FCM 발송에 필요한 최소 모델만 유지합니다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class BidType(str, Enum):
    """입찰 유형 (업종)"""
    SERVICE = "service"           # 용역
    GOODS = "goods"               # 물품
    CONSTRUCTION = "construction" # 공사
    FOREIGN = "foreign"           # 외자

    @property
    def api_suffix(self) -> str:
        """입찰공고정보서비스 API 오퍼레이션 접미사"""
        mapping = {
            BidType.SERVICE: "Servc",
            BidType.GOODS: "Thng",
            BidType.CONSTRUCTION: "Cnstwk",
            BidType.FOREIGN: "Frgcpt",
        }
        return mapping[self]

    @property
    def display_name(self) -> str:
        """한글 표시명"""
        mapping = {
            BidType.SERVICE: "용역",
            BidType.GOODS: "물품",
            BidType.CONSTRUCTION: "공사",
            BidType.FOREIGN: "외자",
        }
        return mapping[self]

    @property
    def topic_category(self) -> str:
        """FCM 토픽 업무구분 코드 (1자)

        토픽 이름에 사용되는 약어:
          service → "s", construction → "c", goods → "g", foreign → "f"
        """
        mapping = {
            BidType.SERVICE: "s",
            BidType.GOODS: "g",
            BidType.CONSTRUCTION: "c",
            BidType.FOREIGN: "f",
        }
        return mapping[self]


class NoticeType(str, Enum):
    """공고 종류"""
    BID = "bid"          # 입찰공고
    PREBID = "prebid"    # 사전규격공개


@dataclass
class BidNotice:
    """입찰공고 정보"""
    bid_ntce_no: str              # 입찰공고번호
    bid_ntce_ord: str             # 입찰공고차수
    bid_ntce_nm: str              # 입찰공고명
    ntce_instt_nm: str            # 공고기관명
    dmnd_instt_nm: str            # 수요기관명
    presmpt_prce: int             # 추정가격 (원)
    bid_ntce_dt: str              # 공고일시
    bid_clse_dt: str              # 입찰마감일시
    openg_dt: str                 # 개찰일시
    bid_ntce_dtl_url: str         # 공고 상세 URL
    prtcpt_psbl_rgn_nm: str       # 참가가능지역명
    bid_type: BidType             # 입찰 유형
    ntce_div_nm: str = ""         # 공고구분명 (일반/긴급 등)
    bid_methd_nm: str = ""        # 입찰방식명
    cntrct_methd_nm: str = ""     # 계약방법명
    sucsfbid_methd_nm: str = ""   # 낙찰방법명
    ntce_instt_cd: str = ""       # 공고기관코드
    dmnd_instt_cd: str = ""       # 수요기관코드
    asign_bdgt_amt: int = 0       # 배정예산액
    bid_begin_dt: str = ""        # 입찰개시일시
    rbid_permsn_yn: str = ""      # 재입찰허용여부

    @property
    def unique_key(self) -> str:
        """중복 판별용 고유 키 (공고번호 + 차수)"""
        return f"{self.bid_ntce_no}-{self.bid_ntce_ord}"

    @property
    def price_display(self) -> str:
        """가격 표시 포맷 (예: 150,000,000원)"""
        if self.presmpt_prce <= 0:
            return "미정"
        return f"{self.presmpt_prce:,}원"


@dataclass
class PreBidNotice:
    """사전규격공개 정보"""
    prcure_no: str                # 사전규격등록번호
    prcure_nm: str                # 사전규격명
    ntce_instt_nm: str            # 공고기관명 (수요기관)
    rcpt_dt: str                  # 공개일(등록일시)
    opnn_reg_clse_dt: str         # 의견등록마감일
    asign_bdgt_amt: int           # 배정예산액
    dtl_url: str                  # 상세 URL
    bid_type: BidType             # 입찰 유형
    prcure_div: str = ""          # 조달구분
    rgst_instt_nm: str = ""       # 등록기관명
    prcure_way: str = ""          # 조달방식

    @property
    def unique_key(self) -> str:
        """중복 판별용 고유 키"""
        return f"{self.prcure_no}"

    @property
    def price_display(self) -> str:
        """가격 표시 포맷 (예: 150,000,000원)"""
        if self.asign_bdgt_amt <= 0:
            return "미정"
        return f"{self.asign_bdgt_amt:,}원"


@dataclass
class KeywordConfig:
    """키워드 설정 (keywords.json에서 로드)"""
    original: str                                  # 원본 키워드
    keyword_hash: str                              # SHA256 해시 (16자 hex)
    exclude: list[str] = field(default_factory=list)  # 제외 키워드
    bid_types: list[str] = field(default_factory=lambda: ["service", "goods", "construction"])

    @property
    def bid_type_enums(self) -> list[BidType]:
        mapping = {
            "service": BidType.SERVICE,
            "goods": BidType.GOODS,
            "construction": BidType.CONSTRUCTION,
            "foreign": BidType.FOREIGN,
        }
        return [mapping[bt] for bt in self.bid_types if bt in mapping]

    def get_topic(self, noti_type: str, bid_type: BidType) -> str:
        """특정 공고유형 + 업무구분에 대한 FCM 토픽 이름 반환

        Args:
            noti_type: "bid" (입찰공고) 또는 "pre" (사전규격)
            bid_type: BidType enum

        Returns:
            FCM 토픽 이름 (예: "bid_s_b29dbba57df61de7")
        """
        return f"{noti_type}_{bid_type.topic_category}_{self.keyword_hash}"


@dataclass
class NotifiedRecord:
    """알림 이력 기록"""
    notified_at: str              # 알림 발송 시각
    keyword: str                  # 매칭 키워드
    notice_type: str = "bid"      # 공고 종류
