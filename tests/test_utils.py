from unittest.mock import patch

import pytest
from raven import Client

from asphalt.sentry.utils import metadata_providers, report_exception


@pytest.mark.asyncio
async def test_report_exception(ctx, component, caplog):
    def fake_provider(context):
        assert context is ctx
        return {'foo': 'bar'}

    def fake_resolve(self, obj):
        assert obj == 'asphalt.core.context.Context'
        return fake_provider

    client = ctx.require_resource(Client)
    assert client.remote.base_url == 'http://127.0.0.1'
    with patch.object(client, 'send') as send:
        with patch.object(metadata_providers.__class__, 'resolve', fake_resolve):
            try:
                1 / 0
            except ZeroDivisionError:
                report_exception('Got a boo-boo', ctx=ctx)

    assert send.call_count == 1

    # Test that an error message was logged too
    messages = [record.message for record in caplog.records]
    assert messages == ['Got a boo-boo']


def test_no_exception():
    exc = pytest.raises(Exception, report_exception)
    exc.match('missing "exception" parameter and no current exception context available')


def test_no_client(caplog):
    try:
        1 / 0
    except ZeroDivisionError as e:
        exc = e

    report_exception('message', exc)
    messages = [record.message for record in caplog.records]
    assert messages == ['message']
