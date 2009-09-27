# subprocess - Subprocesses with accessible I/O streams
#
# For more information about this module, see PEP 324.
#
# Copyright (c) 2003-2005 by Peter Astrand <astrand@lysator.liu.se>
#
# Licensed to PSF under a Contributor Agreement.
# See http://www.python.org/2.4/license for licensing details.

r"""subprocess - Subprocesses with accessible I/O streams

This module allows you to spawn processes, connect to their
input/output/error pipes, and obtain their return codes.  This module
intends to replace several other, older modules and functions, like:

os.system
os.spawn*

Information about how the subprocess module can be used to replace these
modules and functions can be found below.



Using the subprocess module
===========================
This module defines one class called Popen:

class Popen(args, bufsize=0, executable=None,
            stdin=None, stdout=None, stderr=None,
            preexec_fn=None, close_fds=False, shell=False,
            cwd=None, env=None, universal_newlines=False,
            startupinfo=None, creationflags=0):


Arguments are:

args should be a string, or a sequence of program arguments.  The
program to execute is normally the first item in the args sequence or
string, but can be explicitly set by using the executable argument.

On UNIX, with shell=False (default): In this case, the Popen class
uses os.execvp() to execute the child program.  args should normally
be a sequence.  A string will be treated as a sequence with the string
as the only item (the program to execute).

On UNIX, with shell=True: If args is a string, it specifies the
command string to execute through the shell.  If args is a sequence,
the first item specifies the command string, and any additional items
will be treated as additional shell arguments.

On Windows: the Popen class uses CreateProcess() to execute the child
program, which operates on strings.  If args is a sequence, it will be
converted to a string using the list2cmdline method.  Please note that
not all MS Windows applications interpret the command line the same
way: The list2cmdline is designed for applications using the same
rules as the MS C runtime.

bufsize, if given, has the same meaning as the corresponding argument
to the built-in open() function: 0 means unbuffered, 1 means line
buffered, any other positive value means use a buffer of
(approximately) that size.  A negative bufsize means to use the system
default, which usually means fully buffered.  The default value for
bufsize is 0 (unbuffered).

stdin, stdout and stderr specify the executed programs' standard
input, standard output and standard error file handles, respectively.
Valid values are PIPE, an existing file descriptor (a positive
integer), an existing file object, and None.  PIPE indicates that a
new pipe to the child should be created.  With None, no redirection
will occur; the child's file handles will be inherited from the
parent.  Additionally, stderr can be STDOUT, which indicates that the
stderr data from the applications should be captured into the same
file handle as for stdout.

If preexec_fn is set to a callable object, this object will be called
in the child process just before the child is executed.

If close_fds is true, all file descriptors except 0, 1 and 2 will be
closed before the child process is executed.

if shell is true, the specified command will be executed through the
shell.

If cwd is not None, the current directory will be changed to cwd
before the child is executed.

If env is not None, it defines the environment variables for the new
process.

If universal_newlines is true, the file objects stdout and stderr are
opened as a text files, but lines may be terminated by any of '\n',
the Unix end-of-line convention, '\r', the Macintosh convention or
'\r\n', the Windows convention.  All of these external representations
are seen as '\n' by the Python program.  Note: This feature is only
available if Python is built with universal newline support (the
default).  Also, the newlines attribute of the file objects stdout,
stdin and stderr are not updated by the communicate() method.

The startupinfo and creationflags, if given, will be passed to the
underlying CreateProcess() function.  They can specify things such as
appearance of the main window and priority for the new process.
(Windows only)


This module also defines some shortcut functions:

call(*popenargs, **kwargs):
    Run command with arguments.  Wait for command to complete, then
    return the returncode attribute.

    The arguments are the same as for the Popen constructor.  Example:

    retcode = call(["ls", "-l"])

check_call(*popenargs, **kwargs):
    Run command with arguments.  Wait for command to complete.  If the
    exit code was zero then return, otherwise raise
    CalledProcessError.  The CalledProcessError object will have the
    return code in the returncode attribute.

    The arguments are the same as for the Popen constructor.  Example:

    check_call(["ls", "-l"])

getstatusoutput(cmd):
    Return (status, output) of executing cmd in a shell.

    Execute the string 'cmd' in a shell with os.popen() and return a 2-tuple
    (status, output).  cmd is actually run as '{ cmd ; } 2>&1', so that the
    returned output will contain output or error messages. A trailing newline
    is stripped from the output. The exit status for the command can be
    interpreted according to the rules for the C function wait().  Example:

    >>> import subprocess
    >>> subprocess.getstatusoutput('ls /bin/ls')
    (0, '/bin/ls')
    >>> subprocess.getstatusoutput('cat /bin/junk')
    (256, 'cat: /bin/junk: No such file or directory')
    >>> subprocess.getstatusoutput('/bin/junk')
    (256, 'sh: /bin/junk: not found')

getoutput(cmd):
    Return output (stdout or stderr) of executing cmd in a shell.

    Like getstatusoutput(), except the exit status is ignored and the return
    value is a string containing the command's output.  Example:

    >>> import subprocess
    >>> subprocess.getoutput('ls /bin/ls')
    '/bin/ls'

check_output(*popenargs, **kwargs):
   Run command with arguments and return its output as a byte string.

   If the exit code was non-zero it raises a CalledProcessError.  The
   CalledProcessError object will have the return code in the returncode
   attribute and output in the output attribute.

   The arguments are the same as for the Popen constructor.  Example:

      output = subprocess.check_output(["ls", "-l", "/dev/null"])


Exceptions
----------
Exceptions raised in the child process, before the new program has
started to execute, will be re-raised in the parent.  Additionally,
the exception object will have one extra attribute called
'child_traceback', which is a string containing traceback information
from the childs point of view.

The most common exception raised is OSError.  This occurs, for
example, when trying to execute a non-existent file.  Applications
should prepare for OSErrors.

A ValueError will be raised if Popen is called with invalid arguments.

check_call() and check_output() will raise CalledProcessError, if the
called process returns a non-zero return code.


Security
--------
Unlike some other popen functions, this implementation will never call
/bin/sh implicitly.  This means that all characters, including shell
metacharacters, can safely be passed to child processes.


Popen objects
=============
Instances of the Popen class have the following methods:

poll()
    Check if child process has terminated.  Returns returncode
    attribute.

wait()
    Wait for child process to terminate.  Returns returncode attribute.

communicate(input=None)
    Interact with process: Send data to stdin.  Read data from stdout
    and stderr, until end-of-file is reached.  Wait for process to
    terminate.  The optional input argument should be a string to be
    sent to the child process, or None, if no data should be sent to
    the child.

    communicate() returns a tuple (stdout, stderr).

    Note: The data read is buffered in memory, so do not use this
    method if the data size is large or unlimited.

The following attributes are also available:

stdin
    If the stdin argument is PIPE, this attribute is a file object
    that provides input to the child process.  Otherwise, it is None.

stdout
    If the stdout argument is PIPE, this attribute is a file object
    that provides output from the child process.  Otherwise, it is
    None.

stderr
    If the stderr argument is PIPE, this attribute is file object that
    provides error output from the child process.  Otherwise, it is
    None.

pid
    The process ID of the child process.

returncode
    The child return code.  A None value indicates that the process
    hasn't terminated yet.  A negative value -N indicates that the
    child was terminated by signal N (UNIX only).


Replacing older functions with the subprocess module
====================================================
In this section, "a ==> b" means that b can be used as a replacement
for a.

Note: All functions in this section fail (more or less) silently if
the executed program cannot be found; this module raises an OSError
exception.

In the following examples, we assume that the subprocess module is
imported with "from subprocess import *".


Replacing /bin/sh shell backquote
---------------------------------
output=`mycmd myarg`
==>
output = Popen(["mycmd", "myarg"], stdout=PIPE).communicate()[0]


Replacing shell pipe line
-------------------------
output=`dmesg | grep hda`
==>
p1 = Popen(["dmesg"], stdout=PIPE)
p2 = Popen(["grep", "hda"], stdin=p1.stdout, stdout=PIPE)
output = p2.communicate()[0]


Replacing os.system()
---------------------
sts = os.system("mycmd" + " myarg")
==>
p = Popen("mycmd" + " myarg", shell=True)
pid, sts = os.waitpid(p.pid, 0)

Note:

* Calling the program through the shell is usually not required.

* It's easier to look at the returncode attribute than the
  exitstatus.

A more real-world example would look like this:

try:
    retcode = call("mycmd" + " myarg", shell=True)
    if retcode < 0:
        print("Child was terminated by signal", -retcode, file=sys.stderr)
    else:
        print("Child returned", retcode, file=sys.stderr)
except OSError as e:
    print("Execution failed:", e, file=sys.stderr)


Replacing os.spawn*
-------------------
P_NOWAIT example:

pid = os.spawnlp(os.P_NOWAIT, "/bin/mycmd", "mycmd", "myarg")
==>
pid = Popen(["/bin/mycmd", "myarg"]).pid


P_WAIT example:

retcode = os.spawnlp(os.P_WAIT, "/bin/mycmd", "mycmd", "myarg")
==>
retcode = call(["/bin/mycmd", "myarg"])


Vector example:

os.spawnvp(os.P_NOWAIT, path, args)
==>
Popen([path] + args[1:])


Environment example:

os.spawnlpe(os.P_NOWAIT, "/bin/mycmd", "mycmd", "myarg", env)
==>
Popen(["/bin/mycmd", "myarg"], env={"PATH": "/usr/bin"})
"""

import sys
mswindows = (sys.platform == "win32")

import io
import os
import traceback
import gc
import signal
import errno
import time
import sys

if mswindows:
    import msvcrt
    from ctypes import c_char_p, byref, windll, c_long, \
        create_string_buffer, sizeof

    # WriteFile, ReadFile and PeekNamedPipe are needed for async I/O on Windows
    # WriteFile and ReadFile can be substituted for the methods in PyWin32 but
    # the PyWin32 PeekNamedPipe functionality is not the same.
    
    # from win32file import WriteFile
    def WriteFile(handle, writedata):
        """
        Windows kernel32.dll WriteFile API
        
        Writes writedata to the specified file or input/output device with the
        given handle. A tuple is returned whose first element indicates failure
        or success of the API call, 1 indicated an error and 0 a successful
        execution.
        """
        cwritedata = c_char_p(writedata)
        byteswritten = c_long(0)
        returncode = windll.kernel32.WriteFile(c_long(handle),
            cwritedata, len(writedata), byref(byteswritten), c_long(0))
        return (1 - returncode, byteswritten.value)

    # from win32file import ReadFile
    def ReadFile(handle, readsize, lpOverlapped = None):
        """
        Windows kernel32.dll ReadFile API
        
        Reads data from the file or input/output device with the given handle.
        A tuple is returned with the first element being the number of bytes
        read and the second the data that was read.
        
        Please note that Windows API may convert \\n newlines to \\r\\n.
        """
        readdata = create_string_buffer(readsize)
        bytesread = c_long(0)
        returncode = windll.kernel32.ReadFile(c_long(handle), byref(readdata),
            c_long(readsize), byref(bytesread), c_long(0))
        read = readdata.value
        if returncode == True and read is None:
            read = ''
        return (bytesread.value, read)
    
    # from win32pipe import PeekNamedPipe
    def PeekNamedPipe(handle, buffersize):
        """
        Windows kernel32.dll ReadFile API
        
        Reads data and status information from the file or input/output device
        with the given handle. A tuple containing the data read, amount of
        bytes read and the remaining bytes left in the message is returned.
        """
        readdata = create_string_buffer(buffersize)
        readbytes = c_long(0)
        available = c_long(0)
        leftthismessage = c_long(0)
        returncode = windll.kernel32.PeekNamedPipe(c_long(handle),
            byref(readdata), buffersize, byref(readbytes), byref(available),
            byref(leftthismessage))
        read = readdata.value
        if returncode == 1 and read is None:
            read = ''
        return (read, available.value, leftthismessage.value)

else:
    import select
    import fcntl


# Exception classes used by this module.
class CalledProcessError(Exception):
    """This exception is raised when a process run by check_call() or
    check_output() returns a non-zero exit status.
    The exit status will be stored in the returncode attribute;
    check_output() will also store the output in the output attribute.
    """
    def __init__(self, returncode, cmd, output=None):
        self.returncode = returncode
        self.cmd = cmd
        self.output = output
    def __str__(self):
        return "Command '%s' returned non-zero exit status %d" % (self.cmd, self.returncode)


if mswindows:
    import threading
    import msvcrt
    if 0: # <-- change this to use pywin32 instead of the _subprocess driver
        import pywintypes
        from win32api import GetStdHandle, STD_INPUT_HANDLE, \
                             STD_OUTPUT_HANDLE, STD_ERROR_HANDLE
        from win32api import GetCurrentProcess, DuplicateHandle, \
                             GetModuleFileName, GetVersion
        from win32con import DUPLICATE_SAME_ACCESS, SW_HIDE
        from win32pipe import CreatePipe
        from win32process import CreateProcess, STARTUPINFO, \
                                 GetExitCodeProcess, STARTF_USESTDHANDLES, \
                                 STARTF_USESHOWWINDOW, CREATE_NEW_CONSOLE
        from win32process import TerminateProcess
        from win32event import WaitForSingleObject, INFINITE, WAIT_OBJECT_0
    else:
        from _subprocess import *
        class STARTUPINFO:
            dwFlags = 0
            hStdInput = None
            hStdOutput = None
            hStdError = None
            wShowWindow = 0
        class pywintypes:
            error = IOError
else:
    import select
    import errno
    import fcntl
    import pickle

__all__ = ["Popen", "PIPE", "STDOUT", "call", "check_call", "getstatusoutput",
           "getoutput", "check_output", "CalledProcessError",
           "ProcessIOWrapper", "ProcessIOWrapper2", "ProcessIOWrapperStdErr",
           "PopenFileIO" ]

try:
    MAXFD = os.sysconf("SC_OPEN_MAX")
except:
    MAXFD = 256

_active = []

def _cleanup():
    for inst in _active[:]:
        res = inst._internal_poll(_deadstate=sys.maxsize)
        if res is not None and res >= 0:
            try:
                _active.remove(inst)
            except ValueError:
                # This can happen if two threads create a new Popen instance.
                # It's harmless that it was already removed, so ignore.
                pass

PIPE = -1
STDOUT = -2


def call(*popenargs, **kwargs):
    """Run command with arguments.  Wait for command to complete, then
    return the returncode attribute.

    The arguments are the same as for the Popen constructor.  Example:

    retcode = call(["ls", "-l"])
    """
    return Popen(*popenargs, **kwargs).wait()


def check_call(*popenargs, **kwargs):
    """Run command with arguments.  Wait for command to complete.  If
    the exit code was zero then return, otherwise raise
    CalledProcessError.  The CalledProcessError object will have the
    return code in the returncode attribute.

    The arguments are the same as for the Popen constructor.  Example:

    check_call(["ls", "-l"])
    """
    retcode = call(*popenargs, **kwargs)
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        raise CalledProcessError(retcode, cmd)
    return 0


def check_output(*popenargs, **kwargs):
    """Run command with arguments and return its output as a byte string.

    If the exit code was non-zero it raises a CalledProcessError.  The
    CalledProcessError object will have the return code in the returncode
    attribute and output in the output attribute.

    The arguments are the same as for the Popen constructor.  Example:

    >>> check_output(["ls", "-l", "/dev/null"])
    'crw-rw-rw- 1 root root 1, 3 Oct 18  2007 /dev/null\n'

    The stdout argument is not allowed as it is used internally.
    To capture standard error in the result, use stderr=subprocess.STDOUT.

    >>> check_output(["/bin/sh", "-c",
                      "ls -l non_existent_file ; exit 0"],
                     stderr=subprocess.STDOUT)
    'ls: non_existent_file: No such file or directory\n'
    """
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')
    process = Popen(*popenargs, stdout=PIPE, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        raise CalledProcessError(retcode, cmd, output=output)
    return output


def list2cmdline(seq):
    """
    Translate a sequence of arguments into a command line
    string, using the same rules as the MS C runtime:

    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       or pipe characters contained within.  A quoted string can be
       embedded in an argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.
    """

    # See
    # http://msdn.microsoft.com/library/en-us/vccelng/htm/progs_12.asp
    result = []
    needquote = False
    for arg in seq:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or ("|" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


# Various tools for executing commands and looking at their output and status.
#
# NB This only works (and is only relevant) for UNIX.

def getstatusoutput(cmd):
    """Return (status, output) of executing cmd in a shell.

    Execute the string 'cmd' in a shell with os.popen() and return a 2-tuple
    (status, output).  cmd is actually run as '{ cmd ; } 2>&1', so that the
    returned output will contain output or error messages.  A trailing newline
    is stripped from the output.  The exit status for the command can be
    interpreted according to the rules for the C function wait().  Example:

    >>> import subprocess
    >>> subprocess.getstatusoutput('ls /bin/ls')
    (0, '/bin/ls')
    >>> subprocess.getstatusoutput('cat /bin/junk')
    (256, 'cat: /bin/junk: No such file or directory')
    >>> subprocess.getstatusoutput('/bin/junk')
    (256, 'sh: /bin/junk: not found')
    """
    pipe = os.popen('{ ' + cmd + '; } 2>&1', 'r')
    text = pipe.read()
    sts = pipe.close()
    if sts is None: sts = 0
    if text[-1:] == '\n': text = text[:-1]
    return sts, text


def getoutput(cmd):
    """Return output (stdout or stderr) of executing cmd in a shell.

    Like getstatusoutput(), except the exit status is ignored and the return
    value is a string containing the command's output.  Example:

    >>> import subprocess
    >>> subprocess.getoutput('ls /bin/ls')
    '/bin/ls'
    """
    return getstatusoutput(cmd)[1]


def ProcessIOWrapper(cmd, mode = 'r', buffering = 1024):
    """
    Returns a class that has the same methods as a file object reading only
    from the stdout output produced from the program. When writing 
    """
    return PopenFileIO(cmd, mode, buffering)

def ProcessIOWrapperStdErr(cmd, mode = 'r', buffering = 1024):
    """
    Returns a class that has the same methods as a file object reading only
    from the stderr output produced from the program.
    """
    return PopenFileIO(cmd, mode, buffering, stderr = True, stdout = False)

def ProcessIOWrapper2(cmd, mode = 'r', buffering = 1024):
    return PopenFileIO(cmd, mode, buffering, stderr = True)

class PopenFileIO(object):
    """
    This class allows a program to act as a stand-in for a file object. 
    """
    validnewlines = ['\n', '\r\n','\r'] #Order is significant.
    newlines = ('\n',)
    buffereddata = ''
    cursor = 0
    closed = False
    isreadable = False
    iswritable = False
    
    def __init__(self, command, mode = 'r', buffering = 1024, stdout = True, stderr = False):
        self.mode = mode
        self._evaluatemode(mode)
        if stderr and stdout:
            self.popenobject = Popen(command, stdout = PIPE, stdin = PIPE, stderr = PIPE)
        elif stderr:
            self.popenobject = Popen(command, stdin = PIPE, stderr = PIPE)
        elif stdout:
            self.popenobject = Popen(command, stdin = PIPE, stdout = PIPE)
        else:
            raise ValueError("stdout and stderr cannot both be False.")
        self.name = command
        self.stdout = stdout
        self.stderr = stderr
        self.buffering = buffering
    
    def __del__(self):
        self.close()

    def __iter__(self, sizehint = -1):
        linebuffer, bytesread = 'x', 0
        while True:
            linebuffer = self.readline()
            bytesread += len(linebuffer)
            yield linebuffer
            if not self.buffereddata or (bytesread >= sizehint and sizehint > 0):
                break

    def __closecheck(self):
        """Raise an error if the pipe has been terminated and I/O closed."""
        # Check to see if the pipe is closed.
        if self.closed:
            raise ValueError( "I/O operation on a closed file.")  

    def __next__(self):
        return self.readline()

    def _evaluatemode(self, mode):
        canhaverw = True
        unmodded = mode
        self.unewlines = 'U' in mode        
        # Append and write mode on a process are identical
        mode = mode.replace('U', '', 1).replace('a', 'w')

        if 'r' in mode:        
            self.isreadable = True
            mode = mode.replace('r', '', 1)
            canhaverw = False
            
        if 'w' in mode and not canhaverw:
            raise ValueError("must have exactly one of read/write/append mode")
        elif 'w' in mode:
            self.iswritable = 'w' in mode or '+' in mode
            mode = mode.replace('w', '', 1)
        
        if '+' in mode:
            self.iswritable = self.isreadable =  True
            mode = mode.replace('+', '', 1)
        
        for notused in ['b', 't']:
            mode = mode.replace(notused, '', 1)
        
        if mode or self.isreadable == False == self.iswritable:
            raise ValueError("invalid mode: " + repr(unmodded))

    def _newlinesearch(self, searchable):
        best = len(searchable) + 1
        bestnewline = None
        for newlinetype in self.validnewlines:
            marker = searchable.find(newlinetype)
            if marker >= 0 and marker < best:
                best = marker
                bestnewline = newlinetype
        if best == len(searchable) + 1:
            best = -1
        return (best, bestnewline)
    
    def _getrawdata(self, maxsize):
        buffer = []
        if self.stdout:
            buffer.append(str(self.popenobject.asyncread(timeout = 1.25, maxsize = maxsize), sys.stdout.encoding))
        if self.stderr:
            buffer.append(str(self.popenobject.asyncread(timeout = 1.25, maxsize = maxsize, stderr = True), sys.stderr.encoding))
        return ''.join(buffer)

    def truncate(self, size = None):
        pass

    def fileno(self):
        """
        Returns the process I.D. number.
        """
        return self.popenobject.pid

    def flush(self):
        """
        Calls self.__closecheck() to emulate the error that a file would
        return if it were closed upon calling flush.
        """
        self.__closecheck()
        if self.stdout:
            self.popenobject.stdout.write('')
    
    def isatty(self):
        """
        Returns False every time as the process is not considered a tty device.
        """
        return False

    def close(self):
        """Terminate the child process."""
        if hasattr(self, 'popenobject'):
            try:
                self.popenobject.terminate()
            except WindowsError as why:
                if why.errno != 13:
                    raise why
        for stream in [ 'stdin', 'stdout', 'stderr' ]:
            try:
                self.popenobject._close(stream)
            except AttributeError:
                pass
        self.closed = True

    def seekable(self):
        """
        Always returns True.
        """
        return True

    def seek(self, pos, whence = 0):
        """
        Skip a specified number of bytes. Whence can only be 0 or 1 and only
        seeking forward is allowed which means if whence is 0, pos must be
        greater than or equal to the current cursor position. If whence is 1,
        pos must be a postive number.
        """
        if (whence == 0 and pos < self.cursor) or \
           (whence == 1 and pos < 0) or whence > 1 or whence < 0:
            raise IOError( "Invalid seek position." )
        if pos == 0:
            return
        elif whence == 0:
            # Calculate distance to that seek point and skip data
            rdata = self.read(size = pos - self.cursor)
        elif whence == 1:
            # Skip amount of data passed
            rdata = self.read(size = pos)
        else:
            raise IOError( "Invalid seek position" )
        # Only move cursor as far as data was read instead of assuming
    
    def tell(self):
        """
        Returns the number of bytes read / the position in the data stream.
        """
        self.__closecheck()
        return self.cursor

    def writable(self):
        return self.iswritable

    def writelines(self, sequence):
        """
        Write the sequence of lines to the process. Does not add newlines to
        the elements of the sequence.
        """
        for line in sequence:
            self.write(line)

    def write(self, data):
        """
        Write data to the child process.
        """
        self.__closecheck()
        if not self.writable():
            raise IOError(9, "Bad file descriptor")
        self.popenobject.asyncwrite(data)

    def readable(self):
        return self.isreadable

    def readlines(self, sizehint = -1):
        """
        Reads approximately sizehint bytes and returns the data broken into
        lines. If sizehint is left at its default value, lines will be
        returned until no more data is returned by the child process.
        """
        return list(self.__iter__(sizehint = sizehint))

    def readline(self):
        """
        Returns the next line from the process as a string. Will contain the
        newline.
        """
        readdata = self.read()
        marker, nltype = self._newlinesearch(readdata)
        if marker >= 0:
            eol = len(nltype) + marker
            linecontent = readdata[:eol]
            rebuffer = readdata[eol:]
            self.cursor -= len(rebuffer)
            self.buffereddata = rebuffer
        else:
            linecontent = readdata
        return linecontent

    def read(self, size = None, updatecursor = True):
        """
        Reads size bytes if it is specified, otherwise data is read from the
        child process until no more data is returned.
        """
        # To be more file-like, I update the object.newlines tuple as needed
        # though I pre-populate it with \n as I am not quite sure how to handle
        # detecting \n newlines before replacing the others without adding
        # code I think would be more or less pointless.
        self.__closecheck()
        if not self.readable():
            raise IOError(9, "Bad file descriptor")
        rdata = self.buffereddata + self._getrawdata(maxsize = size)
        if self.unewlines:
            if '\r\n' in rdata:
                rdata = rdata.replace('\r\n','\n')
                if '\r\n' not in self.newlines:
                    self.newlines = tuple(list(self.newlines) + ['\r\n'])
            if '\r' in rdata:
                rdata = rdata.replace('\r','\n')
                if '\r' not in self.newlines:
                    self.newlines = tuple(list(self.newlines) + ['\r'])
        self.buffereddata = ''
        if updatecursor:
            self.cursor += len(rdata)
        return rdata

class Popen(object):
    def __init__(self, args, bufsize=0, executable=None,
                 stdin=None, stdout=None, stderr=None,
                 preexec_fn=None, close_fds=False, shell=False,
                 cwd=None, env=None, universal_newlines=False,
                 startupinfo=None, creationflags=0):
        """Create new Popen instance."""
        _cleanup()

        self._child_created = False
        if bufsize is None:
            bufsize = 0  # Restore default
        if not isinstance(bufsize, int):
            raise TypeError("bufsize must be an integer")

        if mswindows:
            if preexec_fn is not None:
                raise ValueError("preexec_fn is not supported on Windows "
                                 "platforms")
            if close_fds and (stdin is not None or stdout is not None or
                              stderr is not None):
                raise ValueError("close_fds is not supported on Windows "
                                 "platforms if you redirect stdin/stdout/stderr")
        else:
            # POSIX
            if startupinfo is not None:
                raise ValueError("startupinfo is only supported on Windows "
                                 "platforms")
            if creationflags != 0:
                raise ValueError("creationflags is only supported on Windows "
                                 "platforms")

        self.stdin = None
        self.stdout = None
        self.stderr = None
        self.pid = None
        self.returncode = None
        self.universal_newlines = universal_newlines

        # Input and output objects. The general principle is like
        # this:
        #
        # Parent                   Child
        # ------                   -----
        # p2cwrite   ---stdin--->  p2cread
        # c2pread    <--stdout---  c2pwrite
        # errread    <--stderr---  errwrite
        #
        # On POSIX, the child objects are file descriptors.  On
        # Windows, these are Windows file handles.  The parent objects
        # are file descriptors on both platforms.  The parent objects
        # are None when not using PIPEs. The child objects are None
        # when not redirecting.

        (p2cread, p2cwrite,
         c2pread, c2pwrite,
         errread, errwrite) = self._get_handles(stdin, stdout, stderr)

        self._execute_child(args, executable, preexec_fn, close_fds,
                            cwd, env, universal_newlines,
                            startupinfo, creationflags, shell,
                            p2cread, p2cwrite,
                            c2pread, c2pwrite,
                            errread, errwrite)

        if mswindows:
            if p2cwrite is not None:
                p2cwrite = msvcrt.open_osfhandle(p2cwrite.Detach(), 0)
            if c2pread is not None:
                c2pread = msvcrt.open_osfhandle(c2pread.Detach(), 0)
            if errread is not None:
                errread = msvcrt.open_osfhandle(errread.Detach(), 0)

        if bufsize == 0:
            bufsize = 1  # Nearly unbuffered (XXX for now)
        if p2cwrite is not None:
            self.stdin = io.open(p2cwrite, 'wb', bufsize)
            if self.universal_newlines:
                self.stdin = io.TextIOWrapper(self.stdin)
        if c2pread is not None:
            self.stdout = io.open(c2pread, 'rb', bufsize)
            if universal_newlines:
                self.stdout = io.TextIOWrapper(self.stdout)
        if errread is not None:
            self.stderr = io.open(errread, 'rb', bufsize)
            if universal_newlines:
                self.stderr = io.TextIOWrapper(self.stderr)


    def _translate_newlines(self, data, encoding):
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        return data.decode(encoding)


    def __del__(self, sys=sys):
        if not self._child_created:
            # We didn't get to successfully create a child process.
            return
        # In case the child hasn't been waited on, check if it's done.
        self._internal_poll(_deadstate=sys.maxsize)
        if self.returncode is None and _active is not None:
            # Child is still running, keep us alive until we can wait on it.
            _active.append(self)

    def recv(self, maxsize=None):
        """
        Non-blocking reading of stdout from the child process. It is
        recommended that you use subprocess.Popen.asyncread instead of this
        method.
        """
        return self._recv('stdout', maxsize)
    
    def recv_err(self, maxsize=None):
        """
        Non-blocking reading of stderr from the child process. It is
        recommended that you use subprocess.Popen.asyncread with the stderr
        keyword specified as True.
        """
        return self._recv('stderr', maxsize)

    def listen(self, input='', maxsize=None):
        """
        Sends input, if specified, and returns a tuple containing the number
        of bytes written to the child process, and the output of the child
        process. maxsize represents the number of bytes to read from the
        child process. If it is None, data will be read until a specified
        timeout is reached or no more data can be read.
        """
        bytes_sent = self.send(input)
        out = self.asyncread(timeout=.25, stderr=False, maxsize=maxsize)
        err = self.asyncread(timeout=.25, stderr=True, maxsize=maxsize)
        return (bytes_sent, out, err)

    def _get_conn_maxsize(self, which, maxsize):
        if maxsize is None:
            maxsize = 1024
        elif maxsize < 1:
            maxsize = 1
        return getattr(self, which), maxsize
    
    def _close(self, which):
        getattr(self, which).close()
        setattr(self, which, None)

    def asyncread(self, timeout=.1, raiseonnone = False, timeresolution=5, stderr = False, maxsize = None, chunksize=None):
        """Non-blocking asynchronous reading of the child process.
        
        Read maxsize bytes asynchronously from the process in chunks of
        chunksize bytes. If chunksize is None, the largest possible chunksize,
        generally 1024 bytes, is used. If maxsize is none, this method will
        attempt to read data until the specified timeout in seconds. To make
        me the specified timeout more accurate or less accurate,
        timeresolution can be increased or decreased respectively.
        
        If raiseonnone is True, the method will raise an exception if the
        process appears to be disconnected.
        """
        if maxsize is not None:
            if maxsize < 1:
                maxsize = 1
        else:
            maxsize = -1
        if chunksize is None and maxsize > 0:
            chunksize = maxsize
        if timeresolution < 1:
            timeresolution = 1
        chunks = []
        dataread = ''
        method = self.recv
        if stderr:
            method = self.recv_err
        limit = time.time()+timeout
        while maxsize != 0 and (time.time() < limit or dataread):
            dataread = method(chunksize)
            if dataread is None:
                if raiseonnone:
                    raise Exception("Disconnected")
                else:
                    break
            elif dataread:
                if maxsize > 0:
                    maxsize -= len(dataread)
                    if (chunksize > maxsize):
                        chunksize = maxsize
                chunks.append(dataread)
            else:
                if maxsize == 0 and maxsize is not None:
                    break
                time.sleep(max((limit-time.time())/timeresolution, 0))
        return b''.join(chunks)

    def asyncwrite(self, ioout):
        bytessent = 0

        while ioout:
            sent = self.send(ioout)
            if sent is None:
                raise Exception("Disconnected. Bytes sent: ", bytessent)
            ioout = ioout[sent:]
            bytessent += sent
        return bytessent

    if mswindows:
        def send(self, input):
            """
            Sends data to the child process in a non-blocking manner. Returns
            the number of bytes written.
            """
            if not self.stdin:
                return None
                
            if isinstance(input, str):
                try:
                    input = bytes(input, sys.stdout.encoding)
                except TypeError:
                    input = bytes(input)

            try:
                x = msvcrt.get_osfhandle(self.stdin.fileno())
                (errCode, written) = WriteFile(x, input)
            except ValueError:
                return self._close('stdin')
            except Exception as why:
                if why.errno in (109, errno.ESHUTDOWN):
                    return self._close('stdin')
                raise

            return written

        def _recv(self, which, maxsize):
            conn, maxsize = self._get_conn_maxsize(which, maxsize)
            if conn is None:
                return None
            
            try:
                x = msvcrt.get_osfhandle(conn.fileno())
                (read, nAvail, nMessage) = PeekNamedPipe(x, 0)
                if maxsize < nAvail:
                    nAvail = maxsize
                if nAvail > 0:
                    (errCode, read) = ReadFile(x, nAvail, None)
            except ValueError:
                return self._close(which)
            except Exception as why:
                if why.errno in (109, errno.ESHUTDOWN):
                    return self._close(which)
                raise

            if self.universal_newlines:
                if not isinstance(read, str):
                    read = self._translate_newlines(read, sys.stdin.encoding)
                else:
                    read = read.replace('\r\n', '\n').replace('\r','\n')
            if isinstance(read, str):
                read = bytes(read, sys.stderr.encoding)
            return read

    else:
        def send(self, input):
            """
            Sends data to the child process in a non-blocking manner. Returns
            the number of bytes written.
            """
            if not self.stdin:
                return None

            if isinstance(input, str):
                try:
                    input = bytes(input, sys.stdout.encoding)
                except TypeError:
                    input = bytes(input)

            if not select.select([], [self.stdin], [], 0)[1]:
                return 0

            try:
                written = os.write(self.stdin.fileno(), input)
            except OSError as why:
                if why.errno == errno.EPIPE: #broken pipe
                    return self._close('stdin')
                raise

            return written

        def _recv(self, which, maxsize):
            conn, maxsize = self._get_conn_maxsize(which, maxsize)
            if conn is None:
                print "booo"
                return None
            
            flags = fcntl.fcntl(conn, fcntl.F_GETFL)
            if not conn.closed:
                print "yay"
                print conn
                fcntl.fcntl(conn, fcntl.F_SETFL, flags| os.O_NONBLOCK)

            try:
                if not select.select([conn], [], [], 0)[0]:
                    print "choose me"
                    return ''

                read = conn.read(maxsize)
                if not read:
                    print "close me"
                    return self._close(which)
    
                if self.universal_newlines:
                    if not isinstance(read, str):
                        read = self._translate_newlines(read, sys.stdin.encoding)
                    else:
                        read = read.replace('\r\n', '\n').replace('\r','\n')
                if isinstance(read, str):
                    try:
                        read = bytes(read, sys.stderr.encoding)
                    except TypeError:
                        read = bytes(read)
                return read
            finally:
                if not conn.closed:
                    fcntl.fcntl(conn, fcntl.F_SETFL, flags)

    def communicate(self, input=None):
        """Interact with process: Send data to stdin.  Read data from
        stdout and stderr, until end-of-file is reached.  Wait for
        process to terminate.  The optional input argument should be a
        string to be sent to the child process, or None, if no data
        should be sent to the child.

        communicate() returns a tuple (stdout, stderr)."""

        # Optimization: If we are only using one pipe, or no pipe at
        # all, using select() or threads is unnecessary.
        if [self.stdin, self.stdout, self.stderr].count(None) >= 2:
            stdout = None
            stderr = None
            if self.stdin:
                if input:
                    self.stdin.write(input)
                self.stdin.close()
            elif self.stdout:
                stdout = self.stdout.read()
                self.stdout.close()
            elif self.stderr:
                stderr = self.stderr.read()
                self.stderr.close()
            self.wait()
            return (stdout, stderr)

        return self._communicate(input)


    def poll(self):
        return self._internal_poll()


    if mswindows:
        #
        # Windows methods
        #
        def _get_handles(self, stdin, stdout, stderr):
            """Construct and return tupel with IO objects:
            p2cread, p2cwrite, c2pread, c2pwrite, errread, errwrite
            """
            if stdin is None and stdout is None and stderr is None:
                return (None, None, None, None, None, None)

            p2cread, p2cwrite = None, None
            c2pread, c2pwrite = None, None
            errread, errwrite = None, None

            if stdin is None:
                p2cread = GetStdHandle(STD_INPUT_HANDLE)
                if p2cread is None:
                    p2cread, _ = CreatePipe(None, 0)
            elif stdin == PIPE:
                p2cread, p2cwrite = CreatePipe(None, 0)
            elif isinstance(stdin, int):
                p2cread = msvcrt.get_osfhandle(stdin)
            else:
                # Assuming file-like object
                p2cread = msvcrt.get_osfhandle(stdin.fileno())
            p2cread = self._make_inheritable(p2cread)

            if stdout is None:
                c2pwrite = GetStdHandle(STD_OUTPUT_HANDLE)
                if c2pwrite is None:
                    _, c2pwrite = CreatePipe(None, 0)
            elif stdout == PIPE:
                c2pread, c2pwrite = CreatePipe(None, 0)
            elif isinstance(stdout, int):
                c2pwrite = msvcrt.get_osfhandle(stdout)
            else:
                # Assuming file-like object
                c2pwrite = msvcrt.get_osfhandle(stdout.fileno())
            c2pwrite = self._make_inheritable(c2pwrite)

            if stderr is None:
                errwrite = GetStdHandle(STD_ERROR_HANDLE)
                if errwrite is None:
                    _, errwrite = CreatePipe(None, 0)
            elif stderr == PIPE:
                errread, errwrite = CreatePipe(None, 0)
            elif stderr == STDOUT:
                errwrite = c2pwrite
            elif isinstance(stderr, int):
                errwrite = msvcrt.get_osfhandle(stderr)
            else:
                # Assuming file-like object
                errwrite = msvcrt.get_osfhandle(stderr.fileno())
            errwrite = self._make_inheritable(errwrite)

            return (p2cread, p2cwrite,
                    c2pread, c2pwrite,
                    errread, errwrite)


        def _make_inheritable(self, handle):
            """Return a duplicate of handle, which is inheritable"""
            return DuplicateHandle(GetCurrentProcess(), handle,
                                   GetCurrentProcess(), 0, 1,
                                   DUPLICATE_SAME_ACCESS)


        def _find_w9xpopen(self):
            """Find and return absolut path to w9xpopen.exe"""
            w9xpopen = os.path.join(os.path.dirname(GetModuleFileName(0)),
                                    "w9xpopen.exe")
            if not os.path.exists(w9xpopen):
                # Eeek - file-not-found - possibly an embedding
                # situation - see if we can locate it in sys.exec_prefix
                w9xpopen = os.path.join(os.path.dirname(sys.exec_prefix),
                                        "w9xpopen.exe")
                if not os.path.exists(w9xpopen):
                    raise RuntimeError("Cannot locate w9xpopen.exe, which is "
                                       "needed for Popen to work with your "
                                       "shell or platform.")
            return w9xpopen


        def _execute_child(self, args, executable, preexec_fn, close_fds,
                           cwd, env, universal_newlines,
                           startupinfo, creationflags, shell,
                           p2cread, p2cwrite,
                           c2pread, c2pwrite,
                           errread, errwrite):
            """Execute program (MS Windows version)"""

            if not isinstance(args, str):
                args = list2cmdline(args)

            # Process startup details
            if startupinfo is None:
                startupinfo = STARTUPINFO()
            if None not in (p2cread, c2pwrite, errwrite):
                startupinfo.dwFlags |= STARTF_USESTDHANDLES
                startupinfo.hStdInput = p2cread
                startupinfo.hStdOutput = c2pwrite
                startupinfo.hStdError = errwrite

            if shell:
                startupinfo.dwFlags |= STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = SW_HIDE
                comspec = os.environ.get("COMSPEC", "cmd.exe")
                args = comspec + " /c " + args
                if (GetVersion() >= 0x80000000 or
                        os.path.basename(comspec).lower() == "command.com"):
                    # Win9x, or using command.com on NT. We need to
                    # use the w9xpopen intermediate program. For more
                    # information, see KB Q150956
                    # (http://web.archive.org/web/20011105084002/http://support.microsoft.com/support/kb/articles/Q150/9/56.asp)
                    w9xpopen = self._find_w9xpopen()
                    args = '"%s" %s' % (w9xpopen, args)
                    # Not passing CREATE_NEW_CONSOLE has been known to
                    # cause random failures on win9x.  Specifically a
                    # dialog: "Your program accessed mem currently in
                    # use at xxx" and a hopeful warning about the
                    # stability of your system.  Cost is Ctrl+C won't
                    # kill children.
                    creationflags |= CREATE_NEW_CONSOLE

            # Start the process
            try:
                hp, ht, pid, tid = CreateProcess(executable, args,
                                         # no special security
                                         None, None,
                                         int(not close_fds),
                                         creationflags,
                                         env,
                                         cwd,
                                         startupinfo)
            except pywintypes.error as e:
                # Translate pywintypes.error to WindowsError, which is
                # a subclass of OSError.  FIXME: We should really
                # translate errno using _sys_errlist (or simliar), but
                # how can this be done from Python?
                raise WindowsError(*e.args)

            # Retain the process handle, but close the thread handle
            self._child_created = True
            self._handle = hp
            self.pid = pid
            ht.Close()

            # Child is launched. Close the parent's copy of those pipe
            # handles that only the child should have open.  You need
            # to make sure that no handles to the write end of the
            # output pipe are maintained in this process or else the
            # pipe will not close when the child process exits and the
            # ReadFile will hang.
            if p2cread is not None:
                p2cread.Close()
            if c2pwrite is not None:
                c2pwrite.Close()
            if errwrite is not None:
                errwrite.Close()


        def _internal_poll(self, _deadstate=None):
            """Check if child process has terminated.  Returns returncode
            attribute."""
            if self.returncode is None:
                if WaitForSingleObject(self._handle, 0) == WAIT_OBJECT_0:
                    self.returncode = GetExitCodeProcess(self._handle)
            return self.returncode


        def wait(self):
            """Wait for child process to terminate.  Returns returncode
            attribute."""
            if self.returncode is None:
                obj = WaitForSingleObject(self._handle, INFINITE)
                self.returncode = GetExitCodeProcess(self._handle)
            return self.returncode


        def _readerthread(self, fh, buffer):
            buffer.append(fh.read())


        def _communicate(self, input):
            stdout = None # Return
            stderr = None # Return

            if self.stdout:
                stdout = []
                stdout_thread = threading.Thread(target=self._readerthread,
                                                 args=(self.stdout, stdout))
                stdout_thread.daemon = True
                stdout_thread.start()
            if self.stderr:
                stderr = []
                stderr_thread = threading.Thread(target=self._readerthread,
                                                 args=(self.stderr, stderr))
                stderr_thread.daemon = True
                stderr_thread.start()

            if self.stdin:
                if input is not None:
                    self.stdin.write(input)
                self.stdin.close()

            if self.stdout:
                stdout_thread.join()
            if self.stderr:
                stderr_thread.join()

            # All data exchanged.  Translate lists into strings.
            if stdout is not None:
                stdout = stdout[0]
            if stderr is not None:
                stderr = stderr[0]

            self.wait()
            return (stdout, stderr)

        def send_signal(self, sig):
            """Send a signal to the process
            """
            if sig == signal.SIGTERM:
                self.terminate()
            else:
                raise ValueError("Only SIGTERM is supported on Windows")

        def terminate(self):
            """Terminates the process
            """
            TerminateProcess(self._handle, 1)

        kill = terminate

    else:
        #
        # POSIX methods
        #
        def _get_handles(self, stdin, stdout, stderr):
            """Construct and return tupel with IO objects:
            p2cread, p2cwrite, c2pread, c2pwrite, errread, errwrite
            """
            p2cread, p2cwrite = None, None
            c2pread, c2pwrite = None, None
            errread, errwrite = None, None

            if stdin is None:
                pass
            elif stdin == PIPE:
                p2cread, p2cwrite = os.pipe()
            elif isinstance(stdin, int):
                p2cread = stdin
            else:
                # Assuming file-like object
                p2cread = stdin.fileno()

            if stdout is None:
                pass
            elif stdout == PIPE:
                c2pread, c2pwrite = os.pipe()
            elif isinstance(stdout, int):
                c2pwrite = stdout
            else:
                # Assuming file-like object
                c2pwrite = stdout.fileno()

            if stderr is None:
                pass
            elif stderr == PIPE:
                errread, errwrite = os.pipe()
            elif stderr == STDOUT:
                errwrite = c2pwrite
            elif isinstance(stderr, int):
                errwrite = stderr
            else:
                # Assuming file-like object
                errwrite = stderr.fileno()

            return (p2cread, p2cwrite,
                    c2pread, c2pwrite,
                    errread, errwrite)


        def _set_cloexec_flag(self, fd):
            try:
                cloexec_flag = fcntl.FD_CLOEXEC
            except AttributeError:
                cloexec_flag = 1

            old = fcntl.fcntl(fd, fcntl.F_GETFD)
            fcntl.fcntl(fd, fcntl.F_SETFD, old | cloexec_flag)


        def _close_fds(self, but):
            os.closerange(3, but)
            os.closerange(but + 1, MAXFD)


        def _execute_child(self, args, executable, preexec_fn, close_fds,
                           cwd, env, universal_newlines,
                           startupinfo, creationflags, shell,
                           p2cread, p2cwrite,
                           c2pread, c2pwrite,
                           errread, errwrite):
            """Execute program (POSIX version)"""

            if isinstance(args, str):
                args = [args]
            else:
                args = list(args)

            if shell:
                args = ["/bin/sh", "-c"] + args

            if executable is None:
                executable = args[0]

            # For transferring possible exec failure from child to parent
            # The first char specifies the exception type: 0 means
            # OSError, 1 means some other error.
            errpipe_read, errpipe_write = os.pipe()
            self._set_cloexec_flag(errpipe_write)

            gc_was_enabled = gc.isenabled()
            # Disable gc to avoid bug where gc -> file_dealloc ->
            # write to stderr -> hang.  http://bugs.python.org/issue1336
            gc.disable()
            try:
                self.pid = os.fork()
            except:
                if gc_was_enabled:
                    gc.enable()
                raise
            self._child_created = True
            if self.pid == 0:
                # Child
                try:
                    # Close parent's pipe ends
                    if p2cwrite is not None:
                        os.close(p2cwrite)
                    if c2pread is not None:
                        os.close(c2pread)
                    if errread is not None:
                        os.close(errread)
                    os.close(errpipe_read)

                    # Dup fds for child
                    if p2cread is not None:
                        os.dup2(p2cread, 0)
                    if c2pwrite is not None:
                        os.dup2(c2pwrite, 1)
                    if errwrite is not None:
                        os.dup2(errwrite, 2)

                    # Close pipe fds.  Make sure we don't close the same
                    # fd more than once, or standard fds.
                    if p2cread is not None and p2cread not in (0,):
                        os.close(p2cread)
                    if c2pwrite is not None and c2pwrite not in (p2cread, 1):
                        os.close(c2pwrite)
                    if (errwrite is not None and
                        errwrite not in (p2cread, c2pwrite, 2)):
                        os.close(errwrite)

                    # Close all other fds, if asked for
                    if close_fds:
                        self._close_fds(but=errpipe_write)

                    if cwd is not None:
                        os.chdir(cwd)

                    if preexec_fn:
                        preexec_fn()

                    if env is None:
                        os.execvp(executable, args)
                    else:
                        os.execvpe(executable, args, env)

                except:
                    exc_type, exc_value, tb = sys.exc_info()
                    # Save the traceback and attach it to the exception object
                    exc_lines = traceback.format_exception(exc_type,
                                                           exc_value,
                                                           tb)
                    exc_value.child_traceback = ''.join(exc_lines)
                    os.write(errpipe_write, pickle.dumps(exc_value))

                # This exitcode won't be reported to applications, so it
                # really doesn't matter what we return.
                os._exit(255)

            # Parent
            if gc_was_enabled:
                gc.enable()
            os.close(errpipe_write)
            if p2cread is not None and p2cwrite is not None:
                os.close(p2cread)
            if c2pwrite is not None and c2pread is not None:
                os.close(c2pwrite)
            if errwrite is not None and errread is not None:
                os.close(errwrite)

            # Wait for exec to fail or succeed; possibly raising exception
            data = os.read(errpipe_read, 1048576) # Exceptions limited to 1 MB
            os.close(errpipe_read)
            if data:
                os.waitpid(self.pid, 0)
                child_exception = pickle.loads(data)
                for fd in (p2cwrite, c2pread, errread):
                    if fd is not None:
                        os.close(fd)
                raise child_exception


        def _handle_exitstatus(self, sts):
            if os.WIFSIGNALED(sts):
                self.returncode = -os.WTERMSIG(sts)
            elif os.WIFEXITED(sts):
                self.returncode = os.WEXITSTATUS(sts)
            else:
                # Should never happen
                raise RuntimeError("Unknown child exit status!")


        def _internal_poll(self, _deadstate=None):
            """Check if child process has terminated.  Returns returncode
            attribute."""
            if self.returncode is None:
                try:
                    pid, sts = os.waitpid(self.pid, os.WNOHANG)
                    if pid == self.pid:
                        self._handle_exitstatus(sts)
                except os.error:
                    if _deadstate is not None:
                        self.returncode = _deadstate
            return self.returncode


        def wait(self):
            """Wait for child process to terminate.  Returns returncode
            attribute."""
            if self.returncode is None:
                pid, sts = os.waitpid(self.pid, 0)
                self._handle_exitstatus(sts)
            return self.returncode


        def _communicate(self, input):
            read_set = []
            write_set = []
            stdout = None # Return
            stderr = None # Return

            if self.stdin:
                # Flush stdio buffer.  This might block, if the user has
                # been writing to .stdin in an uncontrolled fashion.
                self.stdin.flush()
                if input:
                    write_set.append(self.stdin)
                else:
                    self.stdin.close()
            if self.stdout:
                read_set.append(self.stdout)
                stdout = []
            if self.stderr:
                read_set.append(self.stderr)
                stderr = []

            input_offset = 0
            while read_set or write_set:
                try:
                    rlist, wlist, xlist = select.select(read_set, write_set, [])
                except select.error as e:
                    if e.args[0] == errno.EINTR:
                        continue
                    raise

                # XXX Rewrite these to use non-blocking I/O on the
                # file objects; they are no longer using C stdio!

                if self.stdin in wlist:
                    # When select has indicated that the file is writable,
                    # we can write up to PIPE_BUF bytes without risk
                    # blocking.  POSIX defines PIPE_BUF >= 512
                    chunk = input[input_offset : input_offset + 512]
                    bytes_written = os.write(self.stdin.fileno(), chunk)
                    input_offset += bytes_written
                    if input_offset >= len(input):
                        self.stdin.close()
                        write_set.remove(self.stdin)

                if self.stdout in rlist:
                    data = os.read(self.stdout.fileno(), 1024)
                    if not data:
                        self.stdout.close()
                        read_set.remove(self.stdout)
                    stdout.append(data)

                if self.stderr in rlist:
                    data = os.read(self.stderr.fileno(), 1024)
                    if not data:
                        self.stderr.close()
                        read_set.remove(self.stderr)
                    stderr.append(data)

            # All data exchanged.  Translate lists into strings.
            if stdout is not None:
                stdout = b"".join(stdout)
            if stderr is not None:
                stderr = b"".join(stderr)

            # Translate newlines, if requested.
            # This also turns bytes into strings.
            if self.universal_newlines:
                if stdout is not None:
                    stdout = self._translate_newlines(stdout,
                                                      self.stdout.encoding)
                if stderr is not None:
                    stderr = self._translate_newlines(stderr,
                                                      self.stderr.encoding)

            self.wait()
            return (stdout, stderr)

        def send_signal(self, sig):
            """Send a signal to the process
            """
            os.kill(self.pid, sig)

        def terminate(self):
            """Terminate the process with SIGTERM
            """
            self.send_signal(signal.SIGTERM)

        def kill(self):
            """Kill the process with SIGKILL
            """
            self.send_signal(signal.SIGKILL)
