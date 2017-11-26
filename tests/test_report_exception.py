import logging

import pytest
from asphalt.core import Context

from asphalt.exceptions import report_exception, ExtrasProvider
from asphalt.exceptions.api import ExceptionReporter


@pytest.mark.parametrize('logger', [
    True, False, 'asphalt.exceptions', logging.getLogger('asphalt.exceptions')
], ids=['autologger', 'nologger', 'strlogger', 'loggerinstance'])
@pytest.mark.parametrize('faulty_extras_provider', [False, True], ids=['goodextras', 'badextras'])
@pytest.mark.parametrize('faulty_reporter', [False, True], ids=['goodreporter', 'badreporter'])
@pytest.mark.asyncio
async def test_report_exception(logger, faulty_extras_provider, faulty_reporter, caplog):
    class DummyReporter(ExceptionReporter):
        def report_exception(self, ctx: Context, exception: BaseException, message: str,
                             extra) -> None:
            nonlocal reported_exception, reported_message
            assert extra == ({} if faulty_extras_provider else {'foo': 'bar'})
            reported_exception = exception
            reported_message = message
            if faulty_reporter:
                raise Exception('bar')

    class DummyProvider(ExtrasProvider):
        def get_extras(self, ctx: Context, reporter: ExceptionReporter):
            if faulty_extras_provider:
                raise Exception('foo')
            else:
                return {'foo': 'bar'}

    class EmptyProvider(ExtrasProvider):
        def get_extras(self, ctx: Context, reporter: ExceptionReporter):
            return None

    reported_exception = reported_message = None
    async with Context() as ctx:
        ctx.add_resource(DummyReporter(), types=[ExceptionReporter])
        ctx.add_resource(DummyProvider(), 'dummy', types=[ExtrasProvider])
        ctx.add_resource(EmptyProvider(), 'empty', types=[ExtrasProvider])
        try:
            1 / 0
        except ZeroDivisionError as e:
            report_exception(ctx, 'Got a boo-boo', logger=logger)
            assert reported_exception is e
            assert reported_message == 'Got a boo-boo'

    if faulty_reporter and logger:
        messages = [record.message for record in caplog.records
                    if record.name == 'asphalt.exceptions']
        assert messages[-1].startswith(
            'error calling exception reporter '
            '(test_report_exception.test_report_exception.<locals>.DummyReporter)')


def test_no_exception():
    exc = pytest.raises(Exception, report_exception, Context(), 'test')
    exc.match('missing "exception" parameter and no current exception present in sys.exc_info()')
