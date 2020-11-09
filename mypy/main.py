from abc import abstractmethod
import typing


#? ============================================================
#!  COROUTINES
#? ============================================================
import asyncio

# DOC on typing.Callable 
#   Callable type; Callable[[int], str] is a function of (int) -> str.
#   The subscription syntax must always be used with exactly two values: 
#       the argument list and the return type.

# For typing.Coroutine:
#   third item of tuple is the return type
#   should be in order: 
#       1) what you'd get back if you sent a value  ==> doesnt seem to make much difference what we pass in here
#       2) what value you can send;                 ==> same as above
#       3) what you'd get it you awaited it.
function_sig = typing.Callable[[int], typing.Coroutine[typing.Any, typing.Any, int]]


async def increment(number: int) -> int:
    return number+1


# coro must be a coroutine that takes an int and returns an int 
def run_aw(coro: function_sig, number: int) -> None:
    new = asyncio.run(coro(number))
    print(new)

run_aw(increment, 1)




#? ============================================================
#!  PROTOCOLS
#? ============================================================


class Incrementable(typing.Protocol):

    @abstractmethod     #==> decorator forces all child classes to declare an increment method
    def increment(self) -> None:
        ...


# for classes, Protocol seems to do pretty much the same as ABC
class Gear(Incrementable):

    def __init__(self, current_gear: int):
        self.current_gear = current_gear

    # throw an error if we change the return annotation or return value within the function body
    def increment(self) -> None:
        self.current_gear += 1


class Votes(Incrementable):

    def __init__(self, current_votes: int):
        self.votes = current_votes

    # will throw an error ONLY IF Incrementable.increment was decorated as an abstractmethod


# pylang and mypy will recognize that gear has the increment method 
def shift_gear(gear: Gear):
    gear.increment()

# pylang and mypy will throw errors here
def shift_up(gear: int):
    gear.increment()


def cast_vote(votes: Votes):
    votes.increment()

cast_vote(Votes(10))




#? ============================================================
#!  "LABELED" VARIANTS and CONSTRAINED TYPES
#? ============================================================


# ========================================
# STANDARD
# ========================================

class Nstr(str):
    
    def __init__(self, sym: str):
        self.sym = sym

    def __str__(self):
        # return self.sym
        return f"<{self.__class__.__name__}>:{self.sym}"

    def __repr__(self):
        return f"<{self.__class__.__name__}>:{self.sym}"


class Symbol(Nstr): pass
class Asset(Nstr): pass


# ========================================
# TEST
# ========================================


def print_asset(asset: Asset):
    print(asset)

def print_sym(sym: Symbol):
    print(sym)

print_asset(Asset("BTC"))
print_sym(Symbol("BTC-USD"))


# ========================================
# SUBCLASS PYDANTIC (adds validators)
# ========================================
import pydantic
import re


class PSymbol(pydantic.ConstrainedStr, Nstr):
    regex=re.compile(r'[A-Z]+-[A-Z]+')
    strict=True


class PAsset(pydantic.ConstrainedStr, Nstr):
    regex=re.compile(r'[A-Z]{2,5}')
    strict = True


class Instrument(pydantic.BaseModel):

    symbol: PSymbol
    baseAsset: PAsset
    quoteAsset: PAsset


# see if it throws a `not a valid type` error
symlist = typing.List[PSymbol]
assetlist = typing.List[PAsset]


# ========================================
# TEST
# ========================================


print(PSymbol("BTCUSD"))

try:
    # we are free to pass PSymbol or a plain str, both get validated correctly, BUT:
    # if we pass a plain str, the output will be a plain str
    # if we pass a PSymbol we will also get back a Psymbol on output
    inst = Instrument(symbol=PSymbol("BTC-USD"), baseAsset=PAsset("BTC"), quoteAsset=PAsset("USD"))
    print(inst)
    print(type(inst.symbol))    #==> Psymbol

    inst = Instrument(symbol="BTC-USD", baseAsset="BTC", quoteAsset="USD")
    print(inst)
    print(type(inst.symbol))    #==> str

except pydantic.ValidationError as e:
    raise 
