from enum import Enum
from typing import (
    TypeVar,
    Union
)

B = TypeVar("B", covariant=True)
T = TypeVar("T", covariant=True)

Tag = Union[Enum, str]
