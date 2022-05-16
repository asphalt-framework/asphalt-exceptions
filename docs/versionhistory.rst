Version history
===============

This library adheres to `Semantic Versioning 2.0 <http://semver.org/>`_.

**2.0.0** (2022-03-29)

- **BACKWARDS INCOMPATIBLE** Switched Sentry reporter to use sentry-sdk instead of raven
- Added support for Python 3.10
- Dropped support for Python 3.5 and 3.6
- Fixed error in default exception handler when the context lacks the ``exception`` key

**1.0.0** (2017-11-26)

- Initial release
