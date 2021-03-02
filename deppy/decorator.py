from typing import (
    Callable,
    Dict,
    Optional,
    Type
)

from .di import (
    Container,
    container as c
)
from .scope import Scope
from .type import B, T, Tag


def injectable(
    on_behalf_of: Optional[Type[B]] = None,
    *,
    container: Optional[Container] = None,
    scope: Optional[Scope] = None,
    tag: Optional[Tag] = None,
    params: Optional[Dict[str, str]] = None
) -> Callable[[Type[T]], Type[T]]:
    def wrap(target: Type[T]) -> Type[T]:
        (container or c).register(
            target,
            on_behalf_of=on_behalf_of,
            scope=scope,
            tag=tag,
            params=params
        )
        return target
    return wrap
