from abc import ABCMeta, abstractmethod
from typing import Dict, Any, Optional

from asphalt.core import Context


class ExceptionReporter(metaclass=ABCMeta):
    """
    Interface for services that log exceptions on external systems.

    Exception reporter instances must be made available as resources in the context for them to
    take effect.
    """

    @abstractmethod
    def report_exception(self, ctx: Context, exception: BaseException, message: str,
                         extra: Dict[str, Any]) -> None:
        """
        Report the given exception to an external service.

        Implementors should typically queue an event or something instead of using a synchronous
        operations to send the exception.

        :param ctx: the context in which the exception occurred
        :param exception: an exception
        :param message: an accompanying message
        :param extra: backend specific extra contextual information gathered from extras providers
        """


class ExtrasProvider(metaclass=ABCMeta):
    """
    Interface for a provider of extra data for exception reporters.

    Implementors must check the type of the reporter and provide extra data specific to each
    backend. See the documentation of each reporter class to find out the acceptable data
    structures.

    .. note:: Extras are gathered from providers in an unspecified order. The dicts are then
        merged, so any conflicting keys might be lost.
    """

    @abstractmethod
    def get_extras(self, ctx: Context, reporter: ExceptionReporter) -> Optional[Dict[str, Any]]:
        """
        Return context specific extras for the given exception reporter backend.

        :param ctx: the context in which the exception was raised
        :param reporter: the exception reporter for which to provide extras
        :return: a dict containing backend specific extra data, or ``None`` if no appropriate
            extra data can be provided
        """
