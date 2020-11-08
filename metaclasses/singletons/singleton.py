"""Ensure that we can only create a single object of the class
If we try to create a second instance, return the instance that was created first to the user
"""


#============================================================


class SingletonMeta(type):

    __slots__ = ()


    def __new__(cls, clsname, bases, clsdict):
        """called when class is constructed"""

        if not clsdict.get("__slots__", False):
            raise AttributeError("Please define __slots__ for class : ", clsname)


        if isinstance(cls.__slots__, tuple):
            cls.__slots__ += ("_exists", "_persist_args", "_persist_kwargs", "_singleton")
        if isinstance(cls.__slots__, list):
            cls.__slots__.extend(["exists", "_persist_args", "_persist_kwargs"])


        clsdict["_exists"] = False
        return super().__new__(cls, clsname, bases, clsdict)


    def __call__(cls, *args, **kwargs):
        """called when instance of class is created"""

        if not cls._exists:
            cls._singleton = super().__call__(*args, **kwargs)
            cls._exists = True
            cls._persist_args = args
            cls._persist_kwargs = kwargs
        else:
            print("Instance of Class already exists, refering to initial Instance")

        return cls._singleton



#============================================================
#============================================================



if __name__ == "__main__":

    class Person(metaclass=SingletonMeta):

        __slots__ = ("name", "age",)

        def __init__(self, name, age):
            self.name = name
            self.age = age


    first = Person("First", 10)
    second = Person("Second", 20)

    # Should print "First"
    print(second.name)