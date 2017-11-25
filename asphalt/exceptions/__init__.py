import inspect
import logging
import sys
from typing import Union

from asphalt.core import Context, qualified_name, PluginContainer, callable_name
from typeguard import check_argument_types

__all__ = ('report_exception',)

extras_providers = PluginContainer('asphalt.exceptions.extras_providers')
module_logger = logging.getLogger(__name__)


def report_exception(ctx: Context, message: str, exception: BaseException = None, *,
                     logger: Union[logging.Logger, str] = None) -> None:
    """
    Report an exception to all exception reporters in the given context (and optionally log it too)

    :param ctx: context object to use for adding tags and other contextual information to the
        report, as well as for retrieving the sentry client object
    :param message: a free-form message to pass to the exception reporters (often used to describe
        what was happening when the exception occurred)
    :param exception: the exception to report; retrieved from :func:`sys.exc_info` if omitted
    :param logger: logger instance or logger name to log the exception in, instead of the name of
        the module where the exception was raised

    """
    from asphalt.exceptions.api import ExceptionReporter

    assert check_argument_types()

    if not exception:
        exception = sys.exc_info()[1]
        if not exception:
            raise ValueError('missing "exception" parameter and no current exception present in '
                             'sys.exc_info()')

    if logger is None:
        frame = exception.__traceback__.tb_frame
        module = inspect.getmodule(frame)
        if module:
            logger = logging.getLogger(module.__spec__.name)
        else:  # pragma: no cover
            logger = logging.getLogger(frame.f_globals['__name__'])
    elif isinstance(logger, str):
        logger = logging.getLogger(logger)

    logger.error(message, exc_info=exception)

    try:
        extras_provider = extras_providers.resolve(qualified_name(ctx))
    except LookupError:
        extras_provider = None

    for reporter in ctx.get_resources(ExceptionReporter):
        try:
            extra = extras_provider(ctx, reporter.__class__) if extras_provider else None
        except Exception:
            extra = None
            module_logger.exception('error retrieving exception extras from %s()',
                                    callable_name(extras_provider))

        try:
            reporter.report_exception(ctx, exception, message, extra)
        except Exception:
            module_logger.exception('error calling exception reporter (%s)',
                                    qualified_name(reporter))
