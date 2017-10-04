import pytest
from asphalt.core import Context
from async_generator import async_generator, yield_

from asphalt.sentry.component import SentryComponent


@pytest.fixture
@async_generator
async def ctx():
    async with Context() as ctx:
        await yield_(ctx)


@pytest.fixture
async def component(ctx):
    cmp = SentryComponent(dsn='http://username:password@127.0.0.1/000000')
    await cmp.start(ctx)
    return cmp
