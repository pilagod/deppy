import abc


class Greeter(abc.ABC):
    def greet(self) -> str:
        raise NotImplementedError()
