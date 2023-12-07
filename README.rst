``coroutines`` — Python coroutines without an event loop
========================================================

.. image:: https://github.com/ntessore/coroutines/actions/workflows/test.yml/badge.svg
 :target: https://github.com/ntessore/coroutines/actions/workflows/test.yml

.. image:: https://codecov.io/gh/ntessore/coroutines/graph/badge.svg?token=A6L220NL3Y
 :target: https://codecov.io/gh/ntessore/coroutines

This is a small package which provides tools to run ``async`` functions and
generators without an ``asyncio`` event loop.

The ``coroutines`` module provides functions such as |coroutines.run|_,
|coroutines.gather|_, and |coroutines.sleep|_ that work just like their
``asyncio`` counterparts, but without scheduling any tasks in an external event
loop. For example, the following code was adapted `from the asyncio
documentation`__:

__ https://docs.python.org/3.12/library/asyncio-task.html#asyncio.gather

.. code:: python

    import coroutines

    async def factorial(name, number):
        f = 1
        for i in range(2, number + 1):
            print(f"Task {name}: Compute factorial({number}), currently i={i}...")
            await coroutines.sleep()  # CHANGED: no argument
            f *= i
        print(f"Task {name}: factorial({number}) = {f}")
        return f

    async def main():
        # Schedule three calls *concurrently*:
        L = await coroutines.gather(
            factorial("A", 2),
            factorial("B", 3),
            factorial("C", 4),
        )
        print(L)

    coroutines.run(main())

    # Expected output:
    #
    #     Task A: Compute factorial(2), currently i=2...
    #     Task B: Compute factorial(3), currently i=2...
    #     Task C: Compute factorial(4), currently i=2...
    #     Task A: factorial(2) = 2
    #     Task B: Compute factorial(3), currently i=3...
    #     Task C: Compute factorial(4), currently i=3...
    #     Task B: factorial(3) = 6
    #     Task C: Compute factorial(4), currently i=4...
    #     Task C: factorial(4) = 24
    #     [2, 6, 24]

The example produces the same result as the ``asyncio`` code by simply calling,
suspending, and resuming the coroutines until they are completed. Practically,
the only difference between the ``coroutines`` and ``asyncio`` examples is that
|coroutines.sleep|_ does not take an argument. Because there is no external
event loop, a call to |coroutines.sleep|_ cannot suspend the current chain of
coroutines for a fixed amount of time, but only until it is resumed at the next
iteration.


Running coroutines
------------------

.. _coroutines.run:
.. parsed-literal::

   coroutines.\ **run**\ (*coro*) `# <coroutines.run_>`_

.. |coroutines.run| replace:: ``coroutines.run()``

Run a coroutine from synchronous code.


Suspending coroutines
---------------------

.. _coroutines.sleep:
.. parsed-literal::

   *coroutine* coroutines.\ **sleep**\ () `# <coroutines.sleep_>`_

.. |coroutines.sleep| replace:: ``coroutines.sleep()``

Suspend the current chain of coroutines, allowing another coroutine to run
concurrently.


Concurrent execution
--------------------

.. _coroutines.gather:
.. parsed-literal::

   *coroutine* coroutines.\ **gather**\ (*\*coros, close_on_error=True*) `# <coroutines.gather_>`_

.. |coroutines.gather| replace:: ``coroutines.gather()``

Run the coroutines *coros* concurrently.

Returns a coroutine that loops over *coros*, running each coroutine in turn
until it is suspended or finished.  Execution is suspended after each pass over
*coros*, so that other coroutines can run while the result of ``gather()`` is
awaited.

The result of awaiting ``gather()`` is the aggregate list of returned values.

If *close_on_error* is true, all coroutines are closed if an exception occurs
while ``gather()`` is awaited.  Otherwise, the coroutines are left as they are
when the exception is raised.


Creating awaitables
-------------------

The ``coroutines`` module contains a number of helper functions that turn
regular objects into awaitable variants of themselves.

.. _coroutines.awaitable:
.. parsed-literal::

   *coroutine* coroutines.\ **awaitable**\ (*obj=None*) `# <coroutines.awaitable_>`_

.. |coroutines.awaitable| replace:: ``coroutines.awaitable()``

Create an awaitable variant of *obj*.  Returns a coroutine that returns *obj*
and immediately calls |coroutines.sleep|_.


.. _coroutines.aiterable:
.. parsed-literal::

   *coroutine* coroutines.\ **aiterable**\ (*iterable*) `# <coroutines.aiterable_>`_

.. |coroutines.aiterable| replace:: ``coroutines.aiterable()``

Create an awaitable variant of an iterable.  Returns an asynchronous generator
that yields every item in *iterable* and immediately calls |coroutines.sleep|_
after each.


.. _coroutines.arange:
.. parsed-literal::

   *coroutine* coroutines.\ **arange**\ (*stop*) `# <coroutines.arange_>`_
   *coroutine* coroutines.\ **arange**\ (*start, stop[, step]*)

.. |coroutines.arange| replace:: ``coroutines.arange()``

Create an awaitable variant of |range|_.  Returns an asynchronous generator
that yields every integer in the range and immediately calls
|coroutines.sleep|_ after each.


.. |range| replace:: ``range()``
.. _range: https://docs.python.org/3/library/stdtypes.html#range
