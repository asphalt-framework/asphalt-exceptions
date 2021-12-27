from typing import Dict, Any

from asphalt.core import Context
from raygun4py.raygunprovider import RaygunSender

from asphalt.exceptions.api import ExceptionReporter


class RaygunExceptionReporter(ExceptionReporter):
    """
    Reports exceptions using the Raygun_ service.

    To use this backend, install asphalt-exceptions with the ``raygun`` extra.

    All keyword arguments are directly passed to :class:`raygun4py.raygunprovider.RaygunSender`.

    The extras passed to this backend are passed to
    :meth:`raygun4py.raygunprovider.RaygunSender.send_exception` as keyword arguments.

    .. warning:: The current implementation of this backend sends exceptions synchronously,
        potentially blocking the event loop.

    .. _Raygun: https://raygun.com/
    """

    def __init__(self, api_key: str, **config) -> None:
        self.client = RaygunSender(api_key, config)

    def report_exception(self, ctx: Context, exception: BaseException, message: str,
                         extra: Dict[str, Any]) -> None:
        self.client.send_exception(exception, **extra)
