#
# $Id: exceptions.py 538 2009-11-09 14:51:19Z hat $
#
"""
Automata exceptions.

Partial copy of the Chinetics chinetics.core.exceptions file.
"""

class ToolingError(StandardError):
    """
    Base class for all user-friendly errors in the automata tooling.

    @ivar msg: The error message.
    @type msg: C{str}
    """
    def __init__(self, msg):
        StandardError.__init__(self, msg)
        self.msg = msg

    def __str__(self):
        return self.msg


class ModelError(ToolingError):
    """
    Exception that indicates something is wrong with the input model.
    """
    pass


class InputError(ToolingError):
    """
    Exception that indicates something is wrong with the input provided by
    the user.
    """
    pass


class FileFormatError(ToolingError):
    """
    Exception that indicates a file is in the wrong file format or a wrong
    version of the correct file format.

    @ivar filepath: Filename (possibly including path) of the file that is
                    in the wrong (version of the) format.
    @type filepath: C{str}
    """
    def __init__(self, msg, filepath):
        ToolingError.__init__(self, msg)
        self.filepath = filepath

    def __str__(self):
        return 'File "%s": %s' % (self.filepath, self.msg)
