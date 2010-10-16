
import sys

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


