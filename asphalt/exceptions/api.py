from abc import ABCMeta, abstractmethod

from asphalt.core import Context


class ExceptionReporter(metaclass=ABCMeta):
    """
    Interface for services that log exceptions on external systems.

    Exception reporter instances must be made available as resources in the context for them to
    take effect.
    """

    @abstractmethod
    def report_exception(self, ctx: Context, exception: BaseException, message: str,
                         extra=None) -> None:
        """
        Report the given exception to an external service.

        Implementors should typically queue an event or something instead of using a synchronous
        operations to send the exception.

        :param ctx: the context in which the exception occurred
        :param exception: an exception
        :param message: an accompanying message
        :param extra: backend specific extra contextual information provided by a plugin specific
            to the given context type (can be ``None`` due to a number of reasons)
        """
