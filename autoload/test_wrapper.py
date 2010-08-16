
from ConqueSoleSubprocess import *

import logging
LOG_FILENAME = 'pylog.log' # DEBUG
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG) # DEBUG

shell_output = []

foo = ConqueSoleSubprocess()
foo.open('cmd.exe', { 'LINES' : 48, 'COLUMNS' : 160 })
shell_output += foo.read(0, 10, 5000)

foo.write("dir\r")
shell_output += foo.read(0, 50, 1000)
foo.write("dir\r")
shell_output += foo.read(0, 50, 1000)
foo.write("dir\r")
shell_output += foo.read(0, 50, 1000)
foo.write("dir\r")
shell_output += foo.read(0, 50, 1000)
foo.write("dir\r")
shell_output += foo.read(0, 50, 1000)

foo.close()

logging.debug("==================================================================")
logging.debug("\n".join(shell_output))
logging.debug("==================================================================")

