from collections.abc import Awaitable, Generator

import pytest

import coroutines


def test_sleep():
    # sleep must be a generator containing a bare yield,
    # wrapped in types.coroutine
    s = coroutines.sleep()
    assert isinstance(s, Generator)
    assert s.send(None) is None
    with pytest.raises(StopIteration):
        s.send(None)

    # make sure that sleep() will suspend a coroutine
    async def f():
        await coroutines.sleep()
        return "finished"

    # step through the coroutine and make sure it is suspended once
    coro = f()
    assert coro.send(None) is None  # <- no stopiteration raised here!
    with pytest.raises(StopIteration) as excinfo:
        coro.send(None)
    assert excinfo.value.value == "finished"


def test_awaitable():
    a = coroutines.awaitable()
    assert isinstance(a, Awaitable)
    a.close()

    async def returns_none():
        return await coroutines.awaitable()

    coro = returns_none()
    assert coro.send(None) is None
    with pytest.raises(StopIteration) as excinfo:
        coro.send(None)
    assert excinfo.value.value is None

    obj = object()

    async def returns_obj():
        return await coroutines.awaitable(obj)

    coro = returns_obj()
    assert coro.send(None) is None
    with pytest.raises(StopIteration) as excinfo:
        coro.send(None)
    assert excinfo.value.value is obj


def test_aiterable():
    async def f():
        return [x async for x in coroutines.aiterable([1, 2, 3])]

    # coroutine shall await 3 times
    coro = f()
    for _ in range(3):
        assert coro.send(None) is None
    with pytest.raises(StopIteration) as excinfo:
        coro.send(None)
    assert excinfo.value.value == [1, 2, 3]


def test_arange():
    async def f():
        return [x async for x in coroutines.arange(4, 0, -1)]

    # coroutine shall await 4 times
    coro = f()
    for _ in range(4):
        assert coro.send(None) is None
    with pytest.raises(StopIteration) as excinfo:
        coro.send(None)
    assert excinfo.value.value == [4, 3, 2, 1]


def test_gather():
    async def f1():
        for _ in range(3):
            called.append(1)
            await coroutines.sleep()
        return 1

    async def f2():
        for _ in range(5):
            called.append(2)
            await coroutines.sleep()
        return 2

    async def f3():
        called.append(3)
        return 3

    coro = coroutines.gather(f1(), f2(), f3())
    called = []
    # gather will need 5 loops before returning
    for _ in range(5):
        coro.send(None)
    with pytest.raises(StopIteration) as excinfo:
        coro.send(None)
    results = excinfo.value.value
    assert results == [1, 2, 3]
    assert called == [1, 2, 3, 1, 2, 1, 2, 2, 2]

    # nested calling
    coro = coroutines.gather(
        coroutines.gather(f1(), f2()),
        coroutines.gather(f3()),
    )
    called = []
    for _ in range(5):
        coro.send(None)
    with pytest.raises(StopIteration) as excinfo:
        coro.send(None)
    results = excinfo.value.value
    assert results == [[1, 2], [3]]
    assert called == [1, 2, 3, 1, 2, 1, 2, 2, 2]


def test_gather_close_on_error():
    async def first():
        raise RuntimeError

    async def second():
        return "second"

    # close_on_error is true by default, all coroutines should be closed
    c1, c2 = first(), second()
    coro = coroutines.gather(c1, c2)
    try:
        coro.send(None)
    except RuntimeError:
        pass
    # second coroutine is closed
    try:
        c2.send(None)
    except RuntimeError:
        pass

    # when close_on_error is false, the never_awaited coroutine emit a warning
    c1, c2 = first(), second()
    coro = coroutines.gather(c1, c2, close_on_error=False)
    try:
        coro.send(None)
    except RuntimeError:
        pass
    # second coroutine is not closed and returns its value
    try:
        c2.send(None)
    except StopIteration as exc:
        assert exc.value == "second"


def test_run():
    async def f():
        await coroutines.sleep()
        return "done"

    assert coroutines.run(f()) == "done"


def test_run_types_coroutine():
    import types

    @types.coroutine
    def f():
        yield
        return "done"

    assert coroutines.run(f()) == "done"
