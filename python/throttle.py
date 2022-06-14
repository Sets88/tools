import time
from functools import wraps
from typing import Union
from typing import Any
from collections import OrderedDict


class NotSet:
    pass


not_set = NotSet()


def throttle_by_hash_func(
    period: Union[int, float],
    instance_hash_fn: Union[None, callable] = None
):
    state = OrderedDict()

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            curr_ts = time.time()
            outdated_ts = curr_ts - period
            hash_key = not_set

            if callable(instance_hash_fn):
                hash_key = instance_hash_fn(*args, **kwargs)
            outdated = []

            for key, val in state.items():
                if outdated_ts > val:
                    outdated.append(key)
                    continue
                break

            for key in outdated:
                if key in state:
                    del state[key]

            if not state.get(hash_key):
                state[hash_key] = curr_ts
                return func(*args, **kwargs)
        return wrapper

    return decorator


@throttle_by_hash_func(period=10, instance_hash_fn=lambda arg1: arg1)
def test2(arg1):
    return(arg1)


@throttle_by_hash_func(period=10)
def test(arg1):
    return(arg1)


if __name__ == '__main__':
    assert test('e') == 'e'
    assert test('f') == None

    assert test2('a') == 'a'
    assert test2('a') == None
    assert test2('b') == 'b'
