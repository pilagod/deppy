# deppy [![Build Status](https://travis-ci.com/pilagod/deppy.svg?branch=master)](https://travis-ci.com/pilagod/deppy) [![Coverage Status](https://coveralls.io/repos/github/pilagod/deppy/badge.svg?branch=master)](https://coveralls.io/github/pilagod/deppy?branch=master)

Dependency injection framework for Python

## Installation

```shell
$ pip install deppy
```

## Usage

### Concrete class

```python
from deppy import container, injectable

@injectable()
class Greeter:
    def greet(self) -> str:
        return "Hello"

g = container.get(Greeter)
g.greet() # Hello
```

### Implementation for abstract class

```python
import abc

from deppy import container, injectable

# Should raise NotImplementedError instead of abc.abstractmethod decorator for abstract method due to following mypy issue:
# https://github.com/python/mypy/issues/5374#issuecomment-582093112
class Greeter(abc.ABC):
    def greeter(self) -> str:
        raise NotImplementedError()

@injectable(Greeter)
class GreeterImpl(Greeter):
    def greeter(self) -> str:
        return "Hello"

g = container.get(Greeter)
g.greet() # Hello

# If class is on behalf of abstract class, the class cannot get by itself from container
# check `Multiple implementations` section for more complex use case.
container.get(GreeterImpl) # KeyError
```

### Multiple implementations

```python
import abc

from enum import Enum

from deppy from container, injectable

class Greeter(abc.ABC):
    def greet(self) -> str:
        raise NotImplementedError()

class GreeterType(Enum):
    A = "A"
    B = "B"

@injectable(Greeter, tag=GreeterType.A)
class GreeterA(Greeter):
    def greet(self) -> str:
        return "A"

@injectable(Greeter, tag=GreeterType.B)
class GreeterB(Greeter):
    def greet(self) -> str:
        return "B"

a = container.get(Greeter, tag=GreeterType.A)
a.greet() # A

b = container.get(Greeter, tag=GreeterType.B)
b.greet() # B
```

### Dependency injection

```python
from deppy import container, injectable

@injectable()
class Greeter:
    def greet(self) -> str:
        return "Hello"

@injectable()
class GreeterWorld:
    def __init__(self, greeter: Greeter):
        self._greeter = greeter
    
    def greet(self) -> str:
        return self._greeter.greet() + " World"

gw = container.get(GreeterWorld)
gw.greet() # Hello World
```

### Dependency injection with selected implementation

```python
import abc

from enum import Enum

from deppy import container, injectable

class Greeter(abc.ABC):
    def greet(self) -> str:
        raise NotImplementedError()

class GreeterType(Enum):
    A = "A"
    B = "B"
        
@injectable(Greeter, tag=GreeterType.A)
class GreeterA(Greeter):
    def greet(self) -> str:
        return "A"

@injectable(Greeter, tag=GreeterType.B)
class GreeterB(Greeter):
    def greet(self) -> str:
        return "B"

@injectable(
    params={
        "a": GreeterType.A,
        "b": GreeterType.B 
    }
)
class GreeterManager:
    def __init__(self, a: Greeter, b: Greeter):
        self._a = a
        self._b = b

    def greet(self) -> str:
        return self._a.greet() + self._b.greet()

gm = container.get(GreeterManager)
gm.greet() # AB
```

## License

© Cyan Ho (pilagod), 2021-NOW

Released under the [MIT License](https://github.com/pilagod/deppy/blob/master/LICENSE)
