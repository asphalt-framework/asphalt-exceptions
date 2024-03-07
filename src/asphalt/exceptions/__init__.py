from typing import Any

from ._api import ExceptionReporter as ExceptionReporter
from ._api import ExtrasProvider as ExtrasProvider
from ._component import ExceptionReporterComponent as ExceptionReporterComponent
from ._utils import report_exception as report_exception

# Re-export imports, so they look like they live directly in this package
key: str
value: Any
for key, value in list(locals().items()):
    if getattr(value, "__module__", "").startswith(f"{__name__}."):
        value.__module__ = __name__
