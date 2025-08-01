import tempfile

import pytest

from attendance import (
    Player, AttendanceBook, WednesdayBonusPolicy, WeekendBonusPolicy,
    BonusPolicyRegistry, GradePolicyRegistry, DefaultGradePolicy, AttendanceManager
)


@pytest.fixture()
def player():
    return Player(1, "Bob")


def test_player_score_and_attendance(player):
    player.mark_attendance(2, 3)  # Wednesday
    player.mark_attendance(5, 2)  # Saturday
    player.mark_attendance(6, 2)  # Sunday
    assert player.attendance[2] == 1
    assert player.attendance[5] == 1
    assert player.attendance[6] == 1
    assert player.point == 7
    assert player.wed_count == 1
    assert player.weekend_count == 2


def test_wednesday_bonus(player):
    player.attendance[2] = 10
    player.point = 10
    policy = WednesdayBonusPolicy()
    policy.apply(player)
    assert player.point == 20


def test_weekend_bonus(player):
    player.attendance[6] = 10
    player.point = 10
    policy = WeekendBonusPolicy()
    policy.apply(player)
    assert player.point == 20


@pytest.mark.parametrize(
    "point, expected_grade",
    [
        (55, 2),  # GOLD
        (35, 1),  # SILVER
        (10, 0),  # NORMAL
    ]
)
def test_grade_policy(player, point, expected_grade):
    player.point = point
    policy = DefaultGradePolicy()
    policy.apply(player)
    assert player.grade == expected_grade


def test_get_grade_label(player):
    assert DefaultGradePolicy.get_label(2) == "GOLD"
    assert DefaultGradePolicy.get_label(1) == "SILVER"
    assert DefaultGradePolicy.get_label(0) == "NORMAL"


def test_attendance_book_record():
    book = AttendanceBook()
    book.record_attendance("Eve", "wednesday")
    player = book.player_map["Eve"]
    assert player.attendance[2] == 1
    assert player.point == 3


def test_apply_policies():
    book = AttendanceBook()
    for _ in range(10):
        book.record_attendance("Frank", "wednesday")
    book.apply_bonus_policies([WednesdayBonusPolicy()])
    assert book.players[0].point == 40

    book.assign_grade([DefaultGradePolicy()])
    assert book.players[0].grade == 1

    book = AttendanceBook()
    for _ in range(10):
        book.record_attendance("Bob", "sunday")
    book.apply_bonus_policies([WeekendBonusPolicy()])
    assert book.players[0].point == 30


def test_display_results(capsys):
    book = AttendanceBook()
    book.record_attendance("Zero", "monday")
    book.record_attendance("One", "wednesday")

    for player in book.players:
        player.point = 10
        player.grade = 0

    book.players[0].wed_count = 0
    book.players[1].wed_count = 1
    book.players[0].weekend_count = 0
    book.players[1].weekend_count = 0

    book.display_results()

    captured = capsys.readouterr()
    assert "Zero" in captured.out
    assert "One" in captured.out


def test_display_removed_players(capsys):
    book = AttendanceBook()
    book.record_attendance("Zero", "monday")
    book.record_attendance("One", "wednesday")

    for player in book.players:
        player.point = 10
        player.grade = 0

    book.players[0].wed_count = 0
    book.players[1].wed_count = 1
    book.players[0].weekend_count = 0
    book.players[1].weekend_count = 0

    book.display_removed_players()

    captured = capsys.readouterr()
    assert "Zero" in captured.out
    assert "One" not in captured.out


def test_registry_autodiscovery():
    bonus_registry = BonusPolicyRegistry()
    grade_registry = GradePolicyRegistry()
    bonus_policies = bonus_registry.get_all()
    grade_policies = grade_registry.get_all()
    assert any(isinstance(p, WednesdayBonusPolicy) for p in bonus_policies)
    assert any(isinstance(p, WeekendBonusPolicy) for p in bonus_policies)
    assert any(isinstance(p, DefaultGradePolicy) for p in grade_policies)


def test_run_full_flow(capsys):
    test_data = """
    Alice wednesday
    """
    with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False) as tmp:
        tmp.write(test_data)
        tmp.flush()

    manager = AttendanceManager(filename=tmp.name)
    manager.run()

    out = capsys.readouterr().out

    assert "NAME : Alice" in out


def test_file_not_found(capsys):
    manager = AttendanceManager(filename="noname")
    manager.run()

    out = capsys.readouterr().out

    assert "파일을 찾을 수 없습니다" in out
