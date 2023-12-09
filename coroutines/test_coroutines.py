import pytest

import coroutines


class run:
    """
    Context manager to run a coroutine with a number of suspensions.
    """

    def __init__(self, coro, resume=0):
        self.coro = coro
        self.resume = resume

    def __enter__(self):
        __tracebackhide__ = True
        for i in range(self.resume):
            try:
                self.coro.send(None)
            except StopIteration:
                raise AssertionError(
                    f"coroutine suspended {i} times, expected {self.resume}"
                )
        try:
            self.coro.send(None)
        except StopIteration as exc:
            return exc.value
        else:
            raise AssertionError(
                f"coroutine did not complete after {self.resume} suspensions"
            )

    def __exit__(self, exc_type, exc_value, traceback):
        pass


def test_sleep():
    # make sure that sleep() suspends once
    with run(coroutines.sleep(), 1) as result:
        assert result is None

    # make sure that sleep() will suspend a coroutine
    async def f():
        await coroutines.sleep()
        return "finished"

    # step through the coroutine and make sure it is suspended once
    with run(f(), 1) as result:
        assert result == "finished"


def test_awaitable():
    with run(coroutines.awaitable(), 1) as result:
        assert result is None

    obj = object()

    with run(coroutines.awaitable(obj), 1) as result:
        assert result is obj


def test_aiterable():
    async def f():
        return [x async for x in coroutines.aiterable([1, 2, 3])]

    # coroutine shall await 3 times
    with run(f(), 3) as result:
        assert result == [1, 2, 3]


def test_arange():
    async def f():
        return [x async for x in coroutines.arange(4, 0, -1)]

    # coroutine shall await 4 times
    with run(f(), 4) as result:
        assert result == [4, 3, 2, 1]


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
    with run(coro, 5) as result:
        assert result == [1, 2, 3]
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
    # with run(coro) as result:
    #     assert result == [[1, 2], [3]]
    #     assert called == [1, 2, 3, 1, 2, 1, 2, 2, 2]


def test_gather_error():
    async def first():
        raise ValueError

    async def second():
        return "second"

    # if first coroutine raises, the second coroutine is left running
    c1, c2 = first(), second()
    with pytest.raises(ValueError):
        with run(coroutines.gather(c1, c2)):
            pass
    # second coroutine is running
    with run(c2) as result:
        assert result == "second"


def test_run():
    async def f():
        await coroutines.sleep()
        return "done"

    assert coroutines.run(f()) == "done"
