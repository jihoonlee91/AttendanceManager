MAX_PLAYERS = 100
NUM_DAYS = 7

BONUS_POINT_WEDNESDAY = BONUS_POINT_WEEKEND = 10
BONUS_THRESHOLD_WEDNESDAY = BONUS_THRESHOLD_WEEKEND = 10

SCORE_GOLD = 50
SCORE_SILVER = 30

GRADE_NORMAL, GRADE_SILVER, GRADE_GOLD = 0, 1, 2
GRADE_LABEL = ["NORMAL", "SILVER", "GOLD"]

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
WEEKEND_INDICES = {SATURDAY_INDEX, SUNDAY_INDEX}


def init_state() -> dict:
    return {
        "player_id_map": {},
        "player_count": 0,
        "names": [""] * MAX_PLAYERS,
        "attendances": [[0] * NUM_DAYS for _ in range(MAX_PLAYERS)],
        "points": [0] * MAX_PLAYERS,
        "grades": [GRADE_NORMAL] * MAX_PLAYERS,
        "wed_counts": [0] * MAX_PLAYERS,
        "weekend_counts": [0] * MAX_PLAYERS,
    }


def get_or_create_player_id(state: dict, name: str) -> int:
    if name not in state["player_id_map"]:
        new_id = state["player_count"] + 1
        state["player_id_map"][name] = new_id
        state["names"][new_id] = name
        state["player_count"] = new_id
    return state["player_id_map"][name]


def record_attendances(state: dict, player_id: int, day: str) -> None:
    if day not in DAY_INDEX_MAP:
        return

    day_index = DAY_INDEX_MAP[day]
    state["attendances"][player_id][day_index] += 1
    state["points"][player_id] += DAY_SCORE_MAP[day]

    if day_index == WEDNESDAY_INDEX:
        state["wed_counts"][player_id] += 1

    if day_index in WEEKEND_INDICES:
        state["weekend_counts"][player_id] += 1


def apply_bonus(state: dict, player_id: int) -> None:
    attendances = state["attendances"][player_id]

    if attendances[WEDNESDAY_INDEX] >= BONUS_THRESHOLD_WEDNESDAY:
        state["points"][player_id] += BONUS_POINT_WEDNESDAY

    if attendances[SATURDAY_INDEX] + attendances[SUNDAY_INDEX] >= BONUS_THRESHOLD_WEEKEND:
        state["points"][player_id] += BONUS_POINT_WEEKEND


def apply_grade(state: dict, player_id: int) -> None:
    score = state["points"][player_id]

    if score >= SCORE_GOLD:
        state["grades"][player_id] = GRADE_GOLD
    elif score >= SCORE_SILVER:
        state["grades"][player_id] = GRADE_SILVER
    else:
        state["grades"][player_id] = GRADE_NORMAL


def display_results(state: dict, player_id: int) -> None:
    name = state["names"][player_id]
    point = state["points"][player_id]
    grade = GRADE_LABEL[state["grades"][player_id]]

    print(f"NAME : {name}, POINT : {point}, GRADE : {grade}")


def display_removed_players(state: dict) -> None:
    print("\nRemoved player\n==============")

    for player_id in range(1, state["player_count"] + 1):
        if (
                state["grades"][player_id] == GRADE_NORMAL
                and state["wed_counts"][player_id] == 0
                and state["weekend_counts"][player_id] == 0
        ):
            print(state["names"][player_id])


def process_attendances_file(state: dict, filename: str) -> None:
    try:
        with open(filename, encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2:
                    name, day = parts
                    player_id = get_or_create_player_id(state, name)
                    record_attendances(state, player_id, day)

            for player_id in range(1, state["player_count"] + 1):
                apply_bonus(state, player_id)
                apply_grade(state, player_id)
                display_results(state, player_id)

            display_removed_players(state)

    except FileNotFoundError:
        print("파일을 찾을 수 없습니다.")


if __name__ == "__main__":
    state = init_state()
    process_attendances_file(state, "attendance_weekday_500.txt")
