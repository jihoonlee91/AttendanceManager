import inspect
import sys
from abc import ABC, abstractmethod
from typing import List, Type

NUM_DAYS = 7
DAY_INDEX_MAP = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}
DAY_SCORE_MAP = {
    "monday": 1,
    "tuesday": 1,
    "wednesday": 3,
    "thursday": 1,
    "friday": 1,
    "saturday": 2,
    "sunday": 2,
}
WEDNESDAY_INDEX = DAY_INDEX_MAP["wednesday"]
SATURDAY_INDEX = DAY_INDEX_MAP["saturday"]
SUNDAY_INDEX = DAY_INDEX_MAP["sunday"]


class Player:
    def __init__(self, player_id: int, name: str):
        self.player_id = player_id
        self.name = name
        self.attendance = [0] * NUM_DAYS
        self.point = 0
        self.grade = 0
        self.wed_count = 0
        self.weekend_count = 0

    def mark_attendance(self, day_index: int, point: int):
        self.attendance[day_index] += 1
        self.point += point

        if day_index == WEDNESDAY_INDEX:
            self.wed_count += 1

        if day_index in {SATURDAY_INDEX, SUNDAY_INDEX}:
            self.weekend_count += 1


class Policy(ABC):
    @abstractmethod
    def apply(self, player: Player):
        ...


class BonusPolicy(Policy):
    @abstractmethod
    def apply(self, player: Player):
        ...


class WednesdayBonusPolicy(BonusPolicy):
    BONUS_POINT = 10
    BONUS_THRESHOLD = 10

    def apply(self, player: Player):
        if player.attendance[WEDNESDAY_INDEX] >= self.BONUS_THRESHOLD:
            player.point += self.BONUS_POINT


class WeekendBonusPolicy(BonusPolicy):
    BONUS_POINT = 10
    BONUS_THRESHOLD = 10

    def apply(self, player: Player):
        if player.attendance[SATURDAY_INDEX] + player.attendance[SUNDAY_INDEX] >= self.BONUS_THRESHOLD:
            player.point += self.BONUS_POINT


class GradePolicy(Policy):
    @abstractmethod
    def apply(self, player: Player):
        ...


class DefaultGradePolicy(GradePolicy):
    GRADES = {
        "GOLD": (50, 2),
        "SILVER": (30, 1),
        "NORMAL": (0, 0)
    }

    def apply(self, player: Player):
        for label, (threshold, grade_code) in sorted(self.GRADES.items(), key=lambda x: x[1], reverse=True):
            if player.point >= threshold:
                player.grade = grade_code
                return

    @classmethod
    def get_label(cls, grade_code: int) -> str:
        for label, (_, code) in cls.GRADES.items():
            if code == grade_code:
                return label


class PolicyRegistry(ABC):
    def __init__(self):
        self._policies = self._discover_once()

    def _discover_once(self) -> List:
        return self._discover(self._target_class())

    @abstractmethod
    def _target_class(self) -> Type:
        ...

    @staticmethod
    def _discover(base_cls: Type) -> List:
        policies = []
        current_module = sys.modules[__name__]
        for _, obj in inspect.getmembers(current_module, inspect.isclass):
            if issubclass(obj, base_cls) and obj not in (base_cls,):
                policies.append(obj())
        return policies

    def get_all(self) -> List:
        return self._policies


class BonusPolicyRegistry(PolicyRegistry):
    def _target_class(self) -> Type:
        return BonusPolicy


class GradePolicyRegistry(PolicyRegistry):
    def _target_class(self) -> Type:
        return GradePolicy


class AttendanceBook:
    def __init__(self):
        self.player_map = {}
        self.players = []

    def get_or_create_player_id(self, name: str) -> int:
        if name not in self.player_map:
            player = Player(len(self.players) + 1, name)
            self.player_map[name] = player
            self.players.append(player)
        return self.player_map[name]

    def record_attendance(self, name: str, day: str):
        player = self.get_or_create_player_id(name)
        player.mark_attendance(DAY_INDEX_MAP[day], DAY_SCORE_MAP[day])

    def apply_bonus_policies(self, policies: List[BonusPolicy]):
        for player in self.players:
            for policy in policies:
                policy.apply(player)

    def assign_grade(self, policies: List[GradePolicy]):
        for player in self.players:
            for policy in policies:
                policy.apply(player)

    def display_results(self):
        for player in self.players:
            label = DefaultGradePolicy.get_label(player.grade)
            print(f"NAME : {player.name}, POINT : {player.point}, GRADE : {label}")

    def display_removed_players(self):
        print("\nRemoved player\n==============")
        for player in self.players:
            if (
                    player.grade == DefaultGradePolicy.GRADES["NORMAL"][1]
                    and player.wed_count == 0
                    and player.weekend_count == 0
            ):
                print(player.name)


class AttendanceManager:
    def __init__(self, filename):
        self.filename = filename
        self.book = AttendanceBook()
        self.bonus_registry = BonusPolicyRegistry()
        self.grade_resistry = GradePolicyRegistry()

    def run(self):
        try:
            with open(self.filename, encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 2:
                        name, day = parts
                        self.book.record_attendance(name, day)

            self.book.apply_bonus_policies(self.bonus_registry.get_all())
            self.book.assign_grade(self.grade_resistry.get_all())
            self.book.display_results()
            self.book.display_removed_players()

        except FileNotFoundError:
            print("파일을 찾을 수 없습니다.")
