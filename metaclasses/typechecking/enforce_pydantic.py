from inspect import signature
import typing
from typing import List
import logging
import inspect

from pydantic import create_model, ValidationError, StrictStr, StrictInt
from typeguard import typechecked


#============================================================


class EnforcePydanticTypes(type):

    __slots__ = ()

    def __new__(cls, clsname, bases, clsdict):
        """
        happens before creating the class
        """
        if not clsdict.get("__slots__", False):
            raise AttributeError("Please define __slots__")
        else:
            logger = logging.getLogger(name=__name__)
            logger.setLevel(level=logging.INFO)
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            console = logging.StreamHandler()
            console.setFormatter(formatter)
            logger.addHandler(console)
            clsdict["logger"] = logger

        return super().__new__(cls, clsname, bases, clsdict)


    def __init__(cls, clsname, bases, clsdict):
        """only created once when we create the class
        """
        attrs = list(clsdict.keys())
        super().__init__(clsname, bases, clsdict)


    def __call__(cls, *args, **kwargs):
        """this is called every time we create an instance of the class
        """

        #========================================
        # Enforce instance attribute types

        if args:
            raise ValueError("Only Keyword Argumetns are accepted")

        sig = signature(cls.__init__)
        for kw in kwargs:
            if not kwargs.get(kw, False):
                raise AttributeError(f"Must set attribute: <{kw}>")

        model_dict = {kw: (sig.parameters[kw].annotation, ...) for kw in kwargs}
        Model = create_model("Test", **model_dict)

        try:
            validated = Model(**{kw: val for kw, val in kwargs.items()})
            kwargs = validated.dict()
        except ValidationError as e:
            raise e
        except Exception as e:
            raise e

        #========================================
        # Enforce instance method annotations

        # get only functions defined in class that are not builtins
        funcs = {k:v for k, v in dict(inspect.getmembers(cls)).items() if not k.startswith("__") and callable(v)}
        # wrap every user function with <typechecked> decorator
        for name, obj in funcs.items():
            setattr(cls, name, typechecked(obj))

        return super().__call__(*args, **kwargs)


#============================================================


class BeingMeta(metaclass=EnforcePydanticTypes):

    __slots__ = ("name", "age", "hobbies")

    def __init__(self):
        pass


#============================================================


class Being(metaclass=EnforcePydanticTypes):

    __slots__ = ("name", "age", "hobbies")


    def __init__(self, name: StrictStr, age: StrictInt, hobbies: List[StrictStr]):
        """
        Use pydantic strict types if you don't want data to be parsed to defined type
        e.g name:str receiving 1.5 will parse it into "1.5"
        """
        self.name = name
        self.age = age
        self.hobbies = hobbies
        self.logger.info(f"Initialiasing Being : {name}")


    def describe(self, name: str, age: int, hobbies: typing.List[str]) -> str:
        txt = f"{name} is {age} years old and likes {hobbies}"
        return txt




#================================================================================
#================================================================================
#================================================================================


if __name__ == "__main__":

    # check that instance init is typed: replace arg with incorrect type to see behavior
    Person = Being(name="First Person", age=100, hobbies=["dancing", "playing", "sleeping"])

    # check that method calls are typed : replace arg with incorrect type to see behavior
    to_print = Person.describe(name="Second Person", age=10, hobbies=["sex", "drugs", "rocknroll"])

    Person.logger.info(to_print)