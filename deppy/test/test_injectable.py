import pytest

from enum import Enum

from ..decorator import injectable
from ..di import container
from ..scope import Scope

from .greeter import Greeter


class TestInjectable:

    @pytest.fixture(autouse=True)
    def setup(self):
        container.reset()

    def test_injectable_should_bind_class_itself_into_container_without_alias(self):
        @injectable()
        class GreeterImpl(Greeter):
            def greet(self) -> str:
                return "Hello"

        greeter = container.get(GreeterImpl)
        assert greeter.greet() == "Hello"

    def test_injectable_should_allow_alias_to_bind_impl_to_interface(self):
        @injectable(Greeter)
        class GreeterImpl(Greeter):
            def greet(self) -> str:
                return "Hello"

        greeter = container.get(Greeter)
        assert greeter.greet() == "Hello"

    def test_injectable_should_inject_dependency(self):
        @injectable(Greeter)
        class GreeterImpl(Greeter):
            def greet(self) -> str:
                return "Hello"

        @injectable()
        class GreeterWorld:
            def __init__(self, greeter: Greeter):
                self._greeter = greeter

            def greet(self) -> str:
                return "{} {}".format(self._greeter.greet(), "World")

        greeter_world = container.get(GreeterWorld)
        assert greeter_world.greet() == "Hello World"

    def test_injectable_should_inject_primitive_dependency_by_arg_name(self):
        @injectable()
        class Conn:
            def __init__(self, DB_HOST: str):
                self.DB_HOST = DB_HOST

        container.register(
            str,
            tag="DB_HOST",
            value="127.0.0.1"
        )

        conn = container.get(Conn)
        assert conn.DB_HOST == "127.0.0.1"

    def test_injectable_should_inject_primitive_dependency_by_arg_tag(self):
        @injectable(
            params={
                "host": "DB_HOST"
            }
        )
        class Conn:
            def __init__(self, host: str):
                self.host = host

        container.register(
            str,
            tag="DB_HOST",
            value="127.0.0.1"
        )

        conn = container.get(Conn)
        assert conn.host == "127.0.0.1"

    # tag

    def test_injectable_should_allow_tag(self):
        @injectable(Greeter)
        class GreeterImpl(Greeter):
            def greet(self) -> str:
                return "Hello"

        @injectable(Greeter, tag="ANOTHER")
        class GreeterAnotherImpl(Greeter):
            def greet(self) -> str:
                return "Hello Another"

        greeter = container.get(Greeter)
        assert greeter.greet() == "Hello"

        greeter_another = container.get(Greeter, tag="ANOTHER")
        assert greeter_another.greet() == "Hello Another"

    def test_injectable_should_allow_enum_tag(self):
        class GreeterType(Enum):
            Another = "ANOTHER"

        @injectable(Greeter)
        class GreeterImpl(Greeter):
            def greet(self) -> str:
                return "Hello"

        @injectable(Greeter, tag=GreeterType.Another)
        class GreeterAnotherImpl(Greeter):
            def greet(self) -> str:
                return "Hello Another"

        greeter = container.get(Greeter)
        assert greeter.greet() == "Hello"

        greeter_another = container.get(Greeter, tag=GreeterType.Another)
        assert greeter_another.greet() == "Hello Another"

    def test_injectable_should_allow_arg_tag(self):
        @injectable(Greeter)
        class GreeterImpl(Greeter):
            def greet(self) -> str:
                return "Hello"

        @injectable(Greeter, tag="ANOTHER")
        class GreeterAnotherImpl(Greeter):
            def greet(self) -> str:
                return "Hello Another"

        @injectable(
            params={
                "greeter_another": "ANOTHER"
            }
        )
        class GreeterManager:
            def __init__(self, greeter: Greeter, greeter_another: Greeter):
                self._greeter = greeter
                self._greeter_another = greeter_another

            def greet(self) -> str:
                return self._greeter.greet()

            def greet_another(self) -> str:
                return self._greeter_another.greet()

        greeter_manager = container.get(GreeterManager)
        assert greeter_manager.greet() == "Hello"
        assert greeter_manager.greet_another() == "Hello Another"

    # container

    def test_injectable_should_allow_setting_specific_container(self):
        c = container.create_scope()

        @injectable(container=c)
        class GreeterImpl(Greeter):
            def greet(self) -> str:
                return "Hello"

        greeter = c.get(GreeterImpl)
        assert greeter.greet() == "Hello"

        with pytest.raises(KeyError):
            container.get(GreeterImpl)

    # scope

    def test_injectable_should_allow_setting_singleton_scope(self):
        @injectable(scope=Scope.Singleton)
        class GreeterImpl(Greeter):
            def greet(self) -> str:
                pass

        g1 = container.get(GreeterImpl)
        g2 = container.get(GreeterImpl)
        g3 = container.create_scope().get(GreeterImpl)

        assert g1 == g2
        assert g1 == g3

    def test_injectable_should_allow_setting_transient_scope(self):
        @injectable(scope=Scope.Transient)
        class GreeterImpl(Greeter):
            def greet(self) -> str:
                pass

        g1 = container.get(GreeterImpl)
        g2 = container.get(GreeterImpl)

        assert g1 != g2

    def test_injectable_should_allow_setting_scope_scope(self):
        @injectable(scope=Scope.Scope)
        class GreeterImpl(Greeter):
            pass

        g = container.get(GreeterImpl)

        sc = container.create_scope()
        sg1 = sc.get(GreeterImpl)
        sg2 = sc.get(GreeterImpl)

        assert sg1 == sg2
        assert sg1 != g
