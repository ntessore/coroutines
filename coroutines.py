"""
Tools for using coroutines outside of an asyncio event loop.
"""

from __future__ import annotations

__all__ = (
    "aiterable",
    "arange",
    "awaitable",
    "gather",
    "run",
    "sleep",
)

from types import coroutine as _coroutine
from typing import TYPE_CHECKING, overload

if TYPE_CHECKING:
    from typing import Any, ParamSpec, TypeVar
    from collections.abc import AsyncIterable, Coroutine, Generator, Iterable

    P = ParamSpec("P")
    T = TypeVar("T")


@_coroutine
def sleep() -> Generator[None, None, None]:
    """
    Suspend the current chain of coroutines.
    """
    yield


@overload
async def awaitable(obj: None = None) -> None: ...
@overload
async def awaitable(obj: T) -> T: ...
async def awaitable(obj: T | None = None) -> T | None:
    """
    Returns *obj* and suspends the current chain of coroutines.
    """
    await sleep()
    return obj


async def aiterable(iterable: Iterable[T]) -> AsyncIterable[T]:
    """
    Returns an async iterable that sleeps after every item.
    """
    for obj in iterable:
        await sleep()
        yield obj


async def arange(*args: int) -> AsyncIterable[int]:
    """
    Async variant of ``range()``.
    """
    for i in range(*args):
        await sleep()
        yield i


async def gather(
    *coroutines: Coroutine[None, None, T],
    close_on_error: bool = True,
) -> list[T]:
    """
    Concurrently gather results from the given coroutines into a list
    with the same order.  If *close_on_error* is true, all coroutines
    are closed when the function returns due to an exception.
    """
    results: list[Any] = [None] * len(coroutines)
    coros: list[Coroutine[None, None, T] | None] = list(coroutines)
    waiting = len(coros)
    try:
        while True:
            for i, coro in enumerate(coros):
                if coro is None:
                    continue
                try:
                    coro.send(None)
                except StopIteration as exc:
                    results[i] = exc.value
                    coros[i] = None
                    waiting -= 1
            if not waiting:
                return results
            await sleep()
    finally:
        if waiting and close_on_error:
            for coro in filter(None, coros):
                coro.close()


def run(coro: Coroutine[None, None, T]) -> T:
    """
    Run a coroutine and return its result.
    """
    while True:
        try:
            coro.send(None)
        except StopIteration as exc:
            return exc.value  # type: ignore [no-any-return]
