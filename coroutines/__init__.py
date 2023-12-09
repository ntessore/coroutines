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

from collections import deque
from types import coroutine as _coroutine
from typing import TYPE_CHECKING, overload

if TYPE_CHECKING:
    from typing import Any, ParamSpec, TypeVar
    from collections.abc import AsyncIterable, Awaitable, Generator, Iterable

    P = ParamSpec("P")
    T = TypeVar("T")


@_coroutine
def _sleep() -> Generator[None, None, None]:
    """
    Low-level implementation of sleep().
    """
    yield


async def sleep() -> None:
    """
    Suspend the current chain of coroutines.
    """
    await _sleep()


@overload
async def awaitable(obj: None = None) -> None: ...
@overload
async def awaitable(obj: T) -> T: ...
async def awaitable(obj: T | None = None) -> T | None:
    """
    Returns *obj* and suspends the current chain of coroutines.
    """
    await _sleep()
    return obj


async def aiterable(iterable: Iterable[T]) -> AsyncIterable[T]:
    """
    Returns an async iterable that sleeps after every item.
    """
    for obj in iterable:
        await _sleep()
        yield obj


async def arange(*args: int) -> AsyncIterable[int]:
    """
    Async variant of ``range()``.
    """
    for i in range(*args):
        await _sleep()
        yield i


async def gather(*aws: Awaitable[T]) -> list[T]:
    """
    Concurrently gather results from the given awaitables into a list
    with the same order.
    """

    results: list[Any]
    queue: deque[tuple[int, Awaitable[T]] | None]

    results = [None] * len(aws)
    queue = deque(enumerate(aws))
    queue.append(None)
    while len(queue) > 1:
        if queue[0] is None:
            await _sleep()
            queue.rotate(-1)
        else:
            index, coro = queue[0]
            try:
                next(coro.__await__())
                queue.rotate(-1)
            except StopIteration as exc:
                results[index] = exc.value
                queue.popleft()
    return results


def run(coro: Awaitable[T]) -> T:
    """
    Run a coroutine and return its result.
    """

    while True:
        try:
            next(coro.__await__())
        except StopIteration as exc:
            return exc.value  # type: ignore [no-any-return]
