from typing import (
    Callable,
    Dict,
    Optional,
    Tuple,
    Type
)

from .registry import (
    Meta,
    Registry
)
from .scope import Scope
from .type import B, T, Tag


class Container:

    @classmethod
    def create(cls, parent: Optional["Container"] = None) -> "Container":
        return cls(parent=parent)

    def __init__(self, parent: Optional["Container"] = None):
        self._parent = parent
        self._registry = Registry()

    # public

    def create_scope(self) -> "Container":
        return Container.create(parent=self)

    def get(self, target: Type[T], *, tag: Optional[Tag] = None) -> T:
        meta, is_self = self._get_meta(target, tag=tag)

        # return cache instance when scope is Singleton
        if meta.scope == Scope.Singleton and meta.instance:
            return meta.instance

        # return cache instance in current container when scope is Scope
        if meta.scope == Scope.Scope and meta.instance and is_self:
            return meta.instance

        instance = self._create_instance(meta)

        # cache instance when scope is Singleton
        if meta.scope == Scope.Singleton:
            meta.instance = instance

        # cache instance in current container when scope is Scope
        if meta.scope == Scope.Scope:
            scope_meta = meta.copy()
            scope_meta.instance = instance
            self._registry.register_meta(
                scope_meta,
                on_behalf_of=target,
                tag=tag
            )

        if instance:
            return instance

        # generic type T is missing when function returns,
        # instance must exist, or it will raise exception while creating instance,
        # this line is only for patching missing generic type T for this function.
        return target()

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
        self._registry.register(
            target,
            on_behalf_of=on_behalf_of,
            factory=factory,
            scope=scope,
            tag=tag,
            value=value,
            params=params,
        )

    def reset(self):
        self._registry = Registry()

    # private

    def _create_instance(self, meta: Meta[T]) -> T:
        if meta.factory:
            return meta.factory()

        if meta.value:
            return meta.value

        args = []
        for _, p in meta.signature.parameters.items():
            arg = self.get(p.annotation, tag=meta.get_tag(p))
            args.append(arg)

        return meta.ctor(*args)

    def _get_meta(self, target: Type[T], *, tag: Optional[Tag] = None) -> Tuple[Meta[T], bool]:
        try:
            is_self = True
            return self._registry.get(target, tag=tag), is_self
        except KeyError as e:
            if not self._parent:
                raise e
            is_self = False
            meta, _ = self._parent._get_meta(target, tag=tag)
            return meta, is_self


container = Container.create()
