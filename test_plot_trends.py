from datetime import datetime

from plot_trends import daily_readings, most_tracked


def reading(day, hour, efficiency):
    return {"time": datetime(2026, 11, day, hour), "efficiency": efficiency}


def test_daily_readings_keeps_last_of_each_day():
    points = [reading(10, 12, 1.0), reading(10, 13, 2.0), reading(11, 13, 3.0)]
    assert list(daily_readings(points).values()) == [2.0, 3.0]


def test_most_tracked_puts_longest_history_first():
    long_history = [reading(10, 13, 1.0), reading(11, 13, 2.0)]
    short_history = [reading(10, 13, 1.0)]
    timelines = {"short": short_history, "long": long_history}
    assert most_tracked(timelines, n=1) == ["long"]


def test_daily_readings_can_use_another_field():
    points = [{"time": datetime(2026, 11, 10, 13), "efficiency": 1.0, "volume": 500.0}]
    assert list(daily_readings(points, "volume").values()) == [500.0]