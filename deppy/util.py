from typing import Any, Type


def is_builtin_type(target: Type[Any]) -> bool:
    try:
        # https://stackoverflow.com/a/17795199
        return target.__module__ in [
            "__builtin__",
            "__builtins__",
            "builtins"
        ]
    except KeyError as e:
        return False
