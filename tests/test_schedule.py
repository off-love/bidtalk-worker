"""
GitHub Actions 실행 스케줄 판단 테스트
"""

from datetime import date, datetime

from src.utils import schedule
from src.utils.time_utils import KST


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=KST)


def test_workflow_dispatch_always_runs():
    assert schedule.should_run_notice_check(event_name="workflow_dispatch") is True
    assert schedule.should_run_prebid(event_name="workflow_dispatch") is True


def test_weekday_night_runs_every_two_hours():
    assert schedule.should_run_notice_check(now=_dt("2026-04-30T19:07:00")) is True
    assert schedule.should_run_notice_check(now=_dt("2026-04-30T21:07:00")) is True
    assert schedule.should_run_notice_check(now=_dt("2026-04-30T07:07:00")) is True

    assert schedule.should_run_notice_check(now=_dt("2026-04-30T20:07:00")) is False
    assert schedule.should_run_notice_check(now=_dt("2026-04-30T06:07:00")) is False


def test_weekday_daytime_runs_every_thirty_minutes():
    assert schedule.should_run_notice_check(now=_dt("2026-04-30T07:37:00")) is True
    assert schedule.should_run_notice_check(now=_dt("2026-04-30T08:07:00")) is True
    assert schedule.should_run_notice_check(now=_dt("2026-04-30T18:37:00")) is True

    assert schedule.should_run_notice_check(now=_dt("2026-04-30T19:37:00")) is False


def test_holiday_runs_only_every_two_hours():
    holiday_dates = {date(2026, 5, 5)}

    assert schedule.should_run_notice_check(
        now=_dt("2026-05-05T09:07:00"),
        holiday_dates=holiday_dates,
    ) is True
    assert schedule.should_run_notice_check(
        now=_dt("2026-05-05T10:07:00"),
        holiday_dates=holiday_dates,
    ) is False
    assert schedule.should_run_notice_check(
        now=_dt("2026-05-05T09:37:00"),
        holiday_dates=holiday_dates,
    ) is False


def test_schedule_string_skips_weekday_only_crons_on_holiday():
    holiday_dates = {date(2026, 5, 5)}

    assert schedule.should_run_notice_check(
        now=_dt("2026-05-05T10:07:00"),
        event_schedule=schedule.WEEKDAY_DAYTIME_TOP_CRON,
        holiday_dates=holiday_dates,
    ) is False
    assert schedule.should_run_notice_check(
        now=_dt("2026-05-05T09:37:00"),
        event_schedule=schedule.WEEKDAY_DAYTIME_HALF_CRON,
        holiday_dates=holiday_dates,
    ) is False
    assert schedule.should_run_notice_check(
        now=_dt("2026-05-05T09:07:00"),
        event_schedule=schedule.ALWAYS_TWO_HOUR_CRON,
        holiday_dates=holiday_dates,
    ) is True


def test_weekend_is_rest_day():
    assert schedule.is_korean_rest_day(_dt("2026-05-02T09:07:00")) is True


def test_prebid_skips_half_hour_cron_only():
    assert schedule.should_run_prebid(
        event_schedule=schedule.ALWAYS_TWO_HOUR_CRON,
    ) is True
    assert schedule.should_run_prebid(
        event_schedule=schedule.WEEKDAY_DAYTIME_TOP_CRON,
    ) is True
    assert schedule.should_run_prebid(
        event_schedule=schedule.WEEKDAY_DAYTIME_HALF_CRON,
    ) is False
