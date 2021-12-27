import inspect
import logging
import sys
from typing import Union, Dict, Any  # noqa: F401

from asphalt.core import Context, qualified_name, merge_config
from typeguard import check_argument_types

from asphalt.exceptions.api import ExtrasProvider

__all__ = ('report_exception',)

module_logger = logging.getLogger(__name__)


def report_exception(ctx: Context, message: str, exception: BaseException = None, *,
                     logger: Union[logging.Logger, str, bool] = True) -> None:
    """
    Report an exception to all exception reporters in the given context (and optionally log it too)

    :param ctx: context object to use for adding tags and other contextual information to the
        report, as well as for retrieving the sentry client object
    :param message: a free-form message to pass to the exception reporters (often used to describe
        what was happening when the exception occurred)
    :param exception: the exception to report; retrieved from :func:`sys.exc_info` if omitted
    :param logger: logger instance or logger name to log the exception in, instead of the name of
        the module where the exception was raised (or ``False`` to skip logging the exception)

    """
    from asphalt.exceptions.api import ExceptionReporter

    assert check_argument_types()

    if not exception:
        exception = sys.exc_info()[1]
        if not exception:
            raise ValueError('missing "exception" parameter and no current exception present in '
                             'sys.exc_info()')

    if isinstance(logger, bool):
        if logger:
            frame = exception.__traceback__.tb_frame
            module = inspect.getmodule(frame)
            if module:
                logger = logging.getLogger(module.__spec__.name)
            else:  # pragma: no cover
                logger = logging.getLogger(frame.f_globals['__name__'])
        else:
            logger = None
    elif isinstance(logger, str):
        logger = logging.getLogger(logger)

    if logger:
        logger.error(message, exc_info=exception)

    extras_providers = ctx.get_resources(ExtrasProvider)
    for reporter in ctx.get_resources(ExceptionReporter):
        extra = {}  # type: Dict[str, Any]
        for provider in extras_providers:
            try:
                new_extra = provider.get_extras(ctx, reporter)
            except Exception:
                module_logger.exception('error retrieving exception extras for %s from %s',
                                        qualified_name(reporter), qualified_name(provider))
            else:
                if isinstance(new_extra, dict):
                    extra = merge_config(extra, new_extra)

        try:
            reporter.report_exception(ctx, exception, message, extra)
        except Exception:
            module_logger.exception('error calling exception reporter (%s)',
                                    qualified_name(reporter))
