""" {{{
FILE:     autoload/conque_term/conque_globals.py
AUTHOR:   Nico Raffo <nicoraffo@gmail.com>
WEBSITE:  http://conque.googlecode.com
MODIFIED: __MODIFIED__
VERSION:  __VERSION__, for Vim 7.0
LICENSE:
Conque - Vim terminal/console emulator
Copyright (C) 2009-__YEAR__ Nico Raffo 

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

}}} """

import sys
import logging # DEBUG

CONQUE_LOG_FILENAME = '/home/nraffo/.vim/pylog.log'
#logging.basicConfig(filename=CONQUE_LOG_FILENAME, level=logging.DEBUG) # DEBUG

# shared memory size
CONQUE_SOLE_BUFFER_LENGTH = 1000
CONQUE_SOLE_INPUT_SIZE = 1000
CONQUE_SOLE_STATS_SIZE = 1000
CONQUE_SOLE_COMMANDS_SIZE = 255
CONQUE_SOLE_RESCROLL_SIZE = 255
CONQUE_SOLE_RESIZE_SIZE = 255

# interval of screen redraw
# larger number means less frequent
CONQUE_SOLE_SCREEN_REDRAW = 100

# interval of full buffer redraw
# larger number means less frequent
CONQUE_SOLE_BUFFER_REDRAW = 500

# interval of full output bucket replacement
# larger number means less frequent, 1 = every time
CONQUE_SOLE_MEM_REDRAW = 1000

# PYTHON VERSION
CONQUE_PYTHON_VERSION = sys.version_info[0]

# foolhardy attempt to make unicode string syntax compatible with both python 2 and 3
def u(str_val, str_encoding = 'latin-1', errors = 'strict'):

    if CONQUE_PYTHON_VERSION == 3:
        return str_val

    else:
        return unicode(str_val, str_encoding, errors)

# vim:foldmethod=marker
