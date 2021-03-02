import inspect

from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Optional,
    Type
)

from .scope import Scope
from .type import B, T, Tag
from .util import is_builtin_type


class Meta(Generic[T]):

    def __init__(
        self,
        ctor: Type[T],
        *,
        scope: Optional[Scope] = Scope.Transient,
        factory: Optional[Callable[[], T]] = None,
        value: Optional[T] = None,
        params: Optional[Dict[str, str]] = None
    ):
        self.ctor = ctor
        self.scope = scope
        self.factory = factory
        self.value = value
        self.params = params or {}

        # derived properies

        self.instance: Optional[T] = None

        if is_builtin_type(ctor):
            self.signature = inspect.Signature()
        else:
            self.signature = inspect.signature(ctor)

    def copy(self) -> "Meta[T]":
        meta = Meta[T](
            self.ctor,
            scope=self.scope,
            factory=self.factory,
            value=self.value,
            params={**self.params}
        )
        return meta

    def get_tag(self, param: inspect.Parameter) -> Optional[Tag]:
        if param.name in self.params:
            return self.params[param.name]

        if is_builtin_type(param.annotation):
            return param.name

        return None


class Registry:

    def __init__(self):
        self._registry: Dict[Type[Any], Dict[Tag, Meta[Any]]] = {}

    # public

    def get(
        self,
        target: Type[T],
        *,
        tag: Optional[Tag] = None
    ) -> Meta[T]:
        return self._registry[target][self._get_impl_key(tag)]

    def register(
        self,
        target: Type[T],
        *,
        factory: Optional[Callable[[], T]] = None,
        on_behalf_of: Optional[Type[B]] = None,
        scope: Optional[Scope] = Scope.Transient,
        tag: Optional[Tag] = None,
        value: Optional[T] = None,
        params: Optional[Dict[str, str]] = None
    ) -> None:
        target_key = on_behalf_of or target
        if target_key not in self._registry:
            self._registry[target_key] = {}
        self._registry[target_key][self._get_impl_key(tag)] = Meta(
            target,
            scope=scope,
            factory=factory,
            value=value,
            params=params
        )

    def register_meta(
        self,
        meta: Meta[Any],
        *,
        on_behalf_of: Optional[Type[B]] = None,
        tag: Optional[Tag] = None
    ) -> None:
        target_key = on_behalf_of or meta.ctor
        if target_key not in self._registry:
            self._registry[target_key] = {}
        self._registry[target_key][self._get_impl_key(tag)] = meta

    # private

    def _get_impl_key(self, tag: Optional[Tag] = None) -> Tag:
        return tag if tag else "DEFAULT"
