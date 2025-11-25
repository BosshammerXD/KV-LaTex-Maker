from collections.abc import Callable

def ensure_count[T](current_ids: list[T], desired_count: int, factory: Callable[[int], T], deleter: Callable[[T], None]):
        count_difference = len(current_ids) - desired_count
        if count_difference < 0:
            current_ids.extend(factory(i) for i in range(-count_difference))
        elif count_difference > 0:
            [deleter(current_ids.pop()) for _ in range(count_difference)]