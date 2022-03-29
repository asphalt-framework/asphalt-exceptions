import gc
import logging
from asyncio import sleep
from collections import OrderedDict

import pytest
from asphalt.core.context import Context

from asphalt.exceptions.api import ExceptionReporter
from asphalt.exceptions.component import ExceptionReporterComponent


class DummyExceptionReporter(ExceptionReporter):
    def report_exception(
        self, ctx: Context, exception: BaseException, message: str, extra=None
    ) -> None:
        self.reported_exception = exception


@pytest.mark.parametrize(
    "install_default_handler", [True, False], ids=["default", "nodefault"]
)
@pytest.mark.asyncio
async def test_start(caplog, install_default_handler):
    class DummyReporter(ExceptionReporter):
        def report_exception(
            self, ctx: Context, exception: BaseException, message: str, extra=None
        ) -> None:
            pass

    class DummyReporter2(ExceptionReporter):
        def report_exception(
            self, ctx: Context, exception: BaseException, message: str, extra=None
        ) -> None:
            pass

    caplog.set_level(logging.INFO)
    reporters = OrderedDict(
        [
            ("dummy1", {"backend": DummyReporter}),
            ("dummy2", {"backend": DummyReporter2}),
        ]
    )
    cmp = ExceptionReporterComponent(
        reporters=reporters, install_default_handler=install_default_handler
    )
    async with Context() as ctx:
        await cmp.start(ctx)

    messages = [
        record.message
        for record in caplog.records
        if record.name == "asphalt.exceptions.component"
    ]
    if install_default_handler:
        assert len(messages) == 4
        assert messages[-2] == "Installed default event loop exception handler"
        assert messages[-1] == "Uninstalled default event loop exception handler"
    else:
        assert len(messages) == 2

    assert messages[0] == (
        "Configured exception reporter (dummy1; "
        "class=tests.test_component.test_start.<locals>.DummyReporter)"
    )
    assert messages[1] == (
        "Configured exception reporter (dummy2; "
        "class=tests.test_component.test_start.<locals>.DummyReporter2)"
    )


@pytest.mark.asyncio
async def test_default_exception_handler(event_loop):
    """
    Test that an unawaited Task being garbage collected ends up being processed by the default
    exception handler.

    """

    async def fail_task():
        return 1 / 0

    async with Context() as ctx:
        component = ExceptionReporterComponent(backend=DummyExceptionReporter)
        await component.start(ctx)
        reporter = ctx.get_resource(ExceptionReporter)
        event_loop.create_task(fail_task())
        await sleep(0.1)
        gc.collect()

    assert isinstance(reporter.reported_exception, ZeroDivisionError)


@pytest.mark.asyncio
async def test_default_exception_handler_no_exception(event_loop):
    async with Context() as ctx:
        component = ExceptionReporterComponent(backend=DummyExceptionReporter)
        await component.start(ctx)
        handler = event_loop.get_exception_handler()
        handler(event_loop, {"message": "dummy"})
