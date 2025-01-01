from __future__ import annotations

import gc
import logging
from asyncio import get_running_loop, sleep
from typing import Any

import pytest
import sniffio
from asphalt.core import Context, get_resource_nowait
from pytest import LogCaptureFixture

from asphalt.exceptions import ExceptionReporter, ExceptionReporterComponent

pytestmark = pytest.mark.anyio


class DummyExceptionReporter(ExceptionReporter):
    reported_exception: BaseException

    def report_exception(
        self,
        exception: BaseException,
        message: str,
        extra: dict[str, Any],
    ) -> None:
        self.reported_exception = exception


async def test_start(caplog: LogCaptureFixture) -> None:
    class DummyReporter(ExceptionReporter):
        def report_exception(
            self,
            exception: BaseException,
            message: str,
            xtra: dict[str, Any] | None = None,
        ) -> None:
            pass

    class DummyReporter2(ExceptionReporter):
        def report_exception(
            self,
            exception: BaseException,
            message: str,
            xtra: dict[str, Any] | None = None,
        ) -> None:
            pass

    caplog.set_level(logging.INFO, "asphalt.exceptions")
    reporters: dict[str, dict[str, Any]] = {
        "dummy1": {"backend": DummyReporter},
        "dummy2": {"backend": DummyReporter2},
    }
    install_default_handler = sniffio.current_async_library() == "asyncio"
    cmp = ExceptionReporterComponent(
        reporters=reporters, install_default_handler=install_default_handler
    )
    async with Context():
        await cmp.start()

    if install_default_handler:
        assert len(caplog.messages) == 4
        assert caplog.messages[-2] == "Installed default event loop exception handler"
        assert caplog.messages[-1] == "Uninstalled default event loop exception handler"
    else:
        assert len(caplog.messages) == 2

    assert caplog.messages[0] == (
        "Configured exception reporter (dummy1; "
        "class=tests.test_component.test_start.<locals>.DummyReporter)"
    )
    assert caplog.messages[1] == (
        "Configured exception reporter (dummy2; "
        "class=tests.test_component.test_start.<locals>.DummyReporter2)"
    )


@pytest.mark.parametrize("anyio_backend", ["asyncio"], indirect=True)
async def test_default_exception_handler() -> None:
    """
    Test that an unawaited Task being garbage collected ends up being processed by the
    default exception handler.
    """

    async def fail_task() -> float:
        return 1 / 0

    async with Context():
        component = ExceptionReporterComponent(backend=DummyExceptionReporter)
        await component.start()
        reporter = get_resource_nowait(ExceptionReporter)  # type: ignore[type-abstract]
        task = get_running_loop().create_task(fail_task())
        await sleep(0.1)
        del task
        gc.collect()

    assert isinstance(reporter, DummyExceptionReporter)
    assert isinstance(reporter.reported_exception, ZeroDivisionError)


@pytest.mark.parametrize("anyio_backend", ["asyncio"], indirect=True)
async def test_default_exception_handler_no_exception() -> None:
    async with Context():
        component = ExceptionReporterComponent(backend=DummyExceptionReporter)
        await component.start()
        get_running_loop().call_exception_handler({"message": "dummy"})
