# This file is part of Buildbot.  Buildbot is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright Buildbot Team Members
"""
Utility functions to support transition from "slave"-named API to
"worker"-named.

Use of old API generates Python warning which may be logged, ignored or treated
as an error using Python builtin warnings API.
"""

from future.utils import iteritems

import warnings

from twisted.python.deprecate import getWarningMethod
from twisted.python.deprecate import setWarningMethod

__all__ = (
    "DeprecatedWorkerNameWarning",
    "setupWorkerTransition",
)


_WORKER_WARNING_MARK = "[WORKER]"


# DeprecationWarning or PendingDeprecationWarning may be used as
# the base class, but by default deprecation warnings are disabled in Python,
# so by default old-API usage warnings will be ignored - this is not what
# we want.
class DeprecatedWorkerAPIWarning(Warning):

    """Base class for deprecated API warnings."""


class DeprecatedWorkerNameWarning(DeprecatedWorkerAPIWarning):

    """Warning class for use of deprecated classes, functions, methods
    and attributes.
    """


# Separate warnings about deprecated modules from other deprecated
# identifiers.  Deprecated modules are loaded only once and it's hard to
# predict in tests exact places where warning should be issued (in contrast
# warnings about other identifiers will be issued every usage).
class DeprecatedWorkerModuleWarning(DeprecatedWorkerAPIWarning):

    """Warning class for use of deprecated modules."""


def reportDeprecatedWorkerNameUsage(message, stacklevel=None, filename=None,
                                    lineno=None):
    """Hook that is ran when old API name is used.

    :param stacklevel: stack level relative to the caller's frame.
    Defaults to caller of the caller of this function.
    """

    if filename is None:
        if stacklevel is None:
            # Warning will refer to the caller of the caller of this function.
            stacklevel = 3
        else:
            stacklevel += 2

        warnings.warn(DeprecatedWorkerNameWarning(message), None, stacklevel)

    else:
        assert stacklevel is None

        if lineno is None:
            lineno = 0

        warnings.warn_explicit(
            DeprecatedWorkerNameWarning(message),
            DeprecatedWorkerNameWarning,
            filename, lineno)


def setupWorkerTransition():
    """Hook Twisted deprecation machinery to use custom warning class
    for Worker API deprecation warnings."""

    default_warn_method = getWarningMethod()

    def custom_warn_method(message, category, stacklevel):
        if stacklevel is not None:
            stacklevel += 1
        if _WORKER_WARNING_MARK in message:
            # Message contains our mark - it's Worker API Renaming warning,
            # issue it appropriately.
            message = message.replace(_WORKER_WARNING_MARK, "")
            warnings.warn(
                DeprecatedWorkerNameWarning(message), message, stacklevel)
        else:
            # Other's warning message
            default_warn_method(message, category, stacklevel)

    setWarningMethod(custom_warn_method)


# Enable worker transition hooks
setupWorkerTransition()
