
import conque_sole_subprocess_wrapper
from conque_sole_subprocess_wrapper import *

import logging
LOG_FILENAME = 'pylog.log' # DEBUG
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG) # DEBUG

shell_output = ''

foo = ConqueSoleSubprocessWrapper()
foo.open('cmd.exe')
shell_output += foo.read(500)
shell_output += foo.read(500)

foo.write("dir\r")
shell_output += foo.read(500)
shell_output += foo.read(500)
shell_output += foo.read(500)
shell_output += foo.read(500)
shell_output += foo.read(500)
shell_output += foo.read(500)
shell_output += foo.read(500)
shell_output += foo.read(500)
shell_output += foo.read(500)
shell_output += foo.read(500)
shell_output += foo.read(500)

foo.close()

logging.debug("==================================================================")
logging.debug(shell_output)
logging.debug("==================================================================")

