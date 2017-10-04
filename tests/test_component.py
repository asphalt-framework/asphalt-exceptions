from asyncio import sleep
from unittest.mock import patch

import gc
import pytest
from asphalt.core.context import Context
from raven import Client

from asphalt.sentry.component import SentryComponent


@pytest.mark.asyncio
async def test_start(caplog):
    cmp = SentryComponent(dsn='http://username:password@127.0.0.1/000000')
    async with Context() as ctx:
        await cmp.start(ctx)
        ctx.require_resource(Client)

    records = [record for record in caplog.records if record.name == 'asphalt.sentry.component']
    records.sort(key=lambda r: r.message)
    assert len(records) == 2
    assert records[0].message == 'Started Sentry integration'
    assert records[1].message == 'Stopped Sentry integration'


@pytest.mark.asyncio
async def test_default_exception_handler(event_loop, component: SentryComponent):
    """
    Test that an unawaited Task being garbage collected ends up being processed by the default
    exception handler.

    """
    async def fail_task():
        return 1 / 0

    assert component.client.remote.base_url == 'http://127.0.0.1'
    with patch.object(component.client, 'send') as send:
        task = event_loop.create_task(fail_task())
        del task
        await sleep(0.1)
        gc.collect()

    assert send.call_count == 1
