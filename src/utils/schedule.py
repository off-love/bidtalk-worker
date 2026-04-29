"""
GitHub Actions 실행 간격 제어.

GitHub cron은 UTC 기준이고 공휴일을 직접 알 수 없으므로, 워커 안에서
KST 기준 휴일 여부와 트리거된 cron 패턴을 보고 실제 실행 여부를 결정합니다.
"""

from __future__ import annotations

from datetime import date, datetime
import json
from pathlib import Path

from src.utils.time_utils import KST, now_kst

ALWAYS_TWO_HOUR_CRON = "7 0,2,4,6,8,10,12,14,16,18,20,22 * * *"
WEEKDAY_DAYTIME_TOP_CRON = "7 23,1,3,5,7,9 * * *"
WEEKDAY_DAYTIME_HALF_CRON = "37 22,23,0-9 * * *"

HOLIDAYS_PATH = Path(__file__).parent.parent.parent / "data" / "korean_public_holidays.json"
FALSE_VALUES = {"0", "false", "no", "off"}


def _load_holiday_dates(path: Path = HOLIDAYS_PATH) -> set[date]:
    if not path.exists():
        return set()

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    raw_dates = data.get("dates", {})
    if isinstance(raw_dates, dict):
        raw_dates = raw_dates.keys()

    holidays: set[date] = set()
    for value in raw_dates:
        try:
            holidays.add(date.fromisoformat(value))
        except (TypeError, ValueError):
            continue
    return holidays


def is_korean_rest_day(
    value: datetime | date,
    holiday_dates: set[date] | None = None,
) -> bool:
    """주말 또는 저장소에 등록된 한국 공휴일이면 True를 반환합니다."""
    day = value.date() if isinstance(value, datetime) else value
    holidays = holiday_dates if holiday_dates is not None else _load_holiday_dates()
    return day.weekday() >= 5 or day in holidays


def should_run_notice_check(
    now: datetime | None = None,
    event_name: str = "",
    event_schedule: str = "",
    holiday_dates: set[date] | None = None,
) -> bool:
    """현재 트리거가 실제 공고 체크를 실행해야 하는지 판단합니다."""
    if event_name == "workflow_dispatch":
        return True

    current = (now or now_kst()).astimezone(KST)
    schedule = event_schedule.strip()
    rest_day = is_korean_rest_day(current, holiday_dates)

    if schedule == ALWAYS_TWO_HOUR_CRON:
        return True

    if schedule in {WEEKDAY_DAYTIME_TOP_CRON, WEEKDAY_DAYTIME_HALF_CRON}:
        return not rest_day

    if rest_day:
        return current.minute == 7 and current.hour % 2 == 1

    if current.minute == 37:
        return 7 <= current.hour <= 18

    if current.minute != 7:
        return False

    daytime_top = 8 <= current.hour <= 18
    night_two_hour = current.hour in {1, 3, 5, 7, 19, 21, 23}
    return daytime_top or night_two_hour


def should_run_prebid(event_name: str = "", event_schedule: str = "") -> bool:
    """사전규격은 수동 실행과 :07 실행에서만 처리합니다."""
    if event_name == "workflow_dispatch":
        return True
    return event_schedule.strip() != WEEKDAY_DAYTIME_HALF_CRON


def env_enabled(name: str, default: bool = True) -> bool:
    value = ""
    try:
        import os

        value = os.environ.get(name, "")
    except Exception:
        return default

    if not value.strip():
        return default
    return value.strip().lower() not in FALSE_VALUES
