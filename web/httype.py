from typing import Callable, Dict
from types import CoroutineType
from functools import wraps
import inspect

from typing_extensions import TypedDict
from pydantic import BaseModel, ValidationError

from ..result import Err, Ok, Result



def validate_input(
    user_input: BaseModel,
    expected_input: BaseModel,
    # return type of parser needs to be defined for mypy (subclass TypedDict so we know which fields to expect)
    parser: Callable[..., TypedDict],
):
    def decorator(func: CoroutineType):
        @wraps(func)
        async def wrapper(*args, **kwargs):

            if args:
                print("Warning: Limit use of args to <Client>")

            try:
                valid_user_req = user_input(**kwargs)
                parsed = parser(valid_user_req)
            except ValidationError as e:
                return Err(e)
            except Exception as e:
                raise e

            try:
                valid_exp_req = expected_input(**parsed)
                params = valid_exp_req.dict(exclude_none=True)
                result = await func(*args, **params)
                return Ok(result)
            except ValidationError as e:
                return Err(e)
            except Exception as e:
                raise e

        return wrapper

    return decorator



# needs to be the "most outer" decorator if we also validate input
def validate_output(
    target: Callable,   # if response content is indexed weirdly
    expected_output: BaseModel,
    user_output: BaseModel,
    parser: Callable[..., TypedDict],
):
    def decorator(func: CoroutineType):
        @wraps(func)
        async def wrapper(*args, **kwargs):

            try:
                resp = await func(*args, **kwargs)

                # if we chain it with a validate_input decorator we get a Result
                # if isinstance(resp, Result):
                if resp.is_err():
                    return resp
                else:
                    resp = resp.value

                # different clients will define json as either sync or async method
                if inspect.iscoroutinefunction(resp.json):
                    result = target(await resp.json())
                else:
                    result = target(resp.json())

                valid_exp_res = expected_output(**result)
            except ValidationError as e:
                return Err(e)
            except Exception as e:
                raise e

            try:
                parsed = parser(
                    valid_exp_res,
                    symbol=kwargs.get("symbol", None),
                    symbol_mapping=kwargs.get("symbol_mapping"),
                )

                if parsed.is_err():
                    return parsed

                # user is responsible for returning a valid mapping
                valid_user_res = user_output(**parsed.value)
                return Ok(valid_user_res)
            except ValidationError as e:
                return Err(e)
            except Exception as e:
                raise

        return wrapper

    return decorator
