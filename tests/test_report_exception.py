from __future__ import annotations

import logging
from typing import Any

import pytest
from asphalt.core import Context, add_resource
from pytest import LogCaptureFixture

from asphalt.exceptions import ExceptionReporter, ExtrasProvider, report_exception

pytestmark = pytest.mark.anyio


@pytest.mark.parametrize(
    "logger",
    [True, False, "asphalt.exceptions", logging.getLogger("asphalt.exceptions")],
    ids=["autologger", "nologger", "strlogger", "loggerinstance"],
)
@pytest.mark.parametrize(
    "faulty_extras_provider", [False, True], ids=["goodextras", "badextras"]
)
@pytest.mark.parametrize(
    "faulty_reporter", [False, True], ids=["goodreporter", "badreporter"]
)
async def test_report_exception(
    logger: logging.Logger | str,
    faulty_extras_provider: bool,
    faulty_reporter: bool,
    caplog: LogCaptureFixture,
) -> None:
    reported_exception = reported_message = None

    class DummyReporter(ExceptionReporter):
        def report_exception(
            self, exception: BaseException, message: str, extra: dict[str, Any]
        ) -> None:
            nonlocal reported_exception, reported_message
            assert extra == ({} if faulty_extras_provider else {"foo": "bar"})
            reported_exception = exception
            reported_message = message
            if faulty_reporter:
                raise Exception("bar")

    class DummyProvider(ExtrasProvider):
        def get_extras(self, reporter: ExceptionReporter) -> dict[str, Any]:
            if faulty_extras_provider:
                raise Exception("foo")
            else:
                return {"foo": "bar"}

    class EmptyProvider(ExtrasProvider):
        def get_extras(self, reporter: ExceptionReporter) -> None:
            return None

    async with Context():
        add_resource(DummyReporter(), types=[ExceptionReporter])
        add_resource(DummyProvider(), "dummy", types=[ExtrasProvider])
        add_resource(EmptyProvider(), "empty", types=[ExtrasProvider])
        try:
            1 / 0
        except ZeroDivisionError as e:
            report_exception("Got a boo-boo", logger=logger)
            assert reported_exception is e
            assert reported_message == "Got a boo-boo"

    if faulty_reporter and logger:
        assert caplog.messages[-1].startswith(
            "error calling exception reporter "
            "(tests.test_report_exception.test_report_exception.<locals>.DummyReporter)"
        )


def test_no_exception() -> None:
    exc = pytest.raises(Exception, report_exception, "test")
    exc.match(
        'missing "exception" parameter and no current exception present in '
        "sys.exc_info()"
    )
