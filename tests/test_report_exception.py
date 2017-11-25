import logging
from unittest.mock import patch

import pytest
from asphalt.core import Context

from asphalt.exceptions import report_exception
from asphalt.exceptions.api import ExceptionReporter


@pytest.mark.parametrize('logger', [
    None, 'asphalt.exceptions', logging.getLogger('asphalt.exceptions')
], ids=['autologger', 'strlogger', 'loggerinstance'])
@pytest.mark.parametrize('faulty_extras_provider', [False, True], ids=['goodextras', 'badextras'])
@pytest.mark.parametrize('faulty_reporter', [False, True], ids=['goodreporter', 'badreporter'])
@pytest.mark.asyncio
async def test_report_exception(logger, faulty_extras_provider, faulty_reporter, caplog):
    class DummyReporter(ExceptionReporter):
        def report_exception(self, ctx: Context, exception: BaseException, message: str,
                             extra=None) -> None:
            nonlocal reported_exception, reported_message
            assert extra == (None if faulty_extras_provider else {'foo': 'bar'})
            reported_exception = exception
            reported_message = message
            if faulty_reporter:
                raise Exception('bar')

    def fake_provider(context, reporter_class):
        assert reporter_class is DummyReporter
        if faulty_extras_provider:
            raise Exception('foo')
        else:
            return {'foo': 'bar'}

    def fake_resolve(self, obj):
        assert obj == 'asphalt.core.context.Context'
        return fake_provider

    reported_exception = reported_message = None
    with patch('asphalt.exceptions.extras_providers.__class__.resolve', fake_resolve):
        async with Context() as ctx:
            ctx.add_resource(DummyReporter(), types=[ExceptionReporter])
            try:
                1 / 0
            except ZeroDivisionError as e:
                report_exception(ctx, 'Got a boo-boo', logger=logger)
                assert reported_exception is e
                assert reported_message == 'Got a boo-boo'

    if faulty_reporter:
        messages = [record.message for record in caplog.records
                    if record.name == 'asphalt.exceptions']
        assert messages[-1].startswith(
            'error calling exception reporter '
            '(test_report_exception.test_report_exception.<locals>.DummyReporter)')


def test_no_exception():
    exc = pytest.raises(Exception, report_exception, Context(), 'test')
    exc.match('missing "exception" parameter and no current exception present in sys.exc_info()')
