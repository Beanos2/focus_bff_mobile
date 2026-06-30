from datetime import datetime

def evaluate_session_room_rules(session_end_time: datetime, room_info) -> tuple[float, bool]:

    if not room_info or room_info.status != "active":
        return 1.0, False

    if room_info.valid_from_time is None or room_info.valid_until_time is None:
        return room_info.xp_multiplier, True

    session_time = session_end_time.time()

    if room_info.valid_from_time <= room_info.valid_until_time:
        is_inside_range = room_info.valid_from_time <= session_time <= room_info.valid_until_time
    else:
        is_inside_range = session_time >= room_info.valid_from_time or session_time <= room_info.valid_until_time

    if is_inside_range:
        return room_info.xp_multiplier, True
    else:
        return 1.0, False