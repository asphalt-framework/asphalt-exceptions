Version history
===============

This library adheres to `Semantic Versioning 2.0 <http://semver.org/>`_.

**2.2.0** (2024-01-02)

- Added support for looking up hook callables for the Sentry reporter

**2.1.0** (2023-06-10)

- Removed explicit run-time argument type checks and the ``typeguard`` dependency

**2.0.0** (2022-03-29)

- **BACKWARDS INCOMPATIBLE** Switched Sentry reporter to use sentry-sdk instead of raven
- Added support for Python 3.10
- Dropped support for Python 3.5 and 3.6
- Fixed error in default exception handler when the context lacks the ``exception`` key

**1.0.0** (2017-11-26)

- Initial release
