import pytest

from ..di import Container

from .greeter import Greeter


class GreeterImpl(Greeter):
    message: str = "Hello"

    def greet(self) -> str:
        return self.message


class GreeterAnotherImpl(Greeter):
    message: str = "Hello Another"

    def greet(self) -> str:
        return self.message


class TestContainer:

    # register

    class TestRegister:

        def test_register(self):
            c = Container.create()

            c.register(GreeterImpl)

            greeter = c.get(GreeterImpl)
            assert greeter.greet() == GreeterImpl.message

        def test_register_should_allow_custom_factory(self):
            c = Container.create()

            c.register(Greeter, factory=lambda: GreeterImpl())

            greeter = c.get(Greeter)
            assert greeter.greet() == GreeterImpl.message

        def test_register_should_allow_custom_value(self):
            c = Container.create()

            c.register(Greeter, value=GreeterImpl())

            greeter = c.get(Greeter)
            assert greeter.greet() == GreeterImpl.message

        def test_register_should_give_priority_to_factory_over_value(self):
            c = Container.create()

            c.register(
                Greeter,
                factory=lambda: GreeterImpl(),
                value=Greeter()
            )

            greeter = c.get(Greeter)
            assert greeter.greet() == GreeterImpl.message

    # reset

    class TestReset:

        def test_reset_should_reset_container(self):
            c1 = Container.create()
            c1.register(GreeterImpl)

            c1.reset()

            with pytest.raises(KeyError):
                c1.get(GreeterImpl)

    # scope

    class TestScope:

        def test_create_scope_should_create_new_container_whose_parent_is_creator(self):
            c1 = Container.create()
            c1.register(GreeterImpl, on_behalf_of=Greeter)

            c2 = c1.create_scope()

            greeter = c2.get(Greeter)
            assert greeter.greet() == GreeterImpl.message

        def test_create_scope_should_create_new_container_with_its_own_scope(self):
            c1 = Container.create()
            c1.register(GreeterImpl, on_behalf_of=Greeter)

            c2 = c1.create_scope()
            c2.register(GreeterAnotherImpl, on_behalf_of=Greeter)

            greeter = c1.get(Greeter)
            assert greeter.greet() == GreeterImpl.message

            greeter_another = c2.get(Greeter)
            assert greeter_another.greet() == GreeterAnotherImpl.message
