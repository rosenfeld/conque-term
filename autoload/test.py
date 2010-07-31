import conque_sole_subprocess, logging
from conque_sole_subprocess import *
LOG_FILENAME = 'pylog.log' # DEBUG
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG) # DEBUG

shell_output = ""

foo = ConqueSoleSubprocess()
foo.open('Powershell.exe')
shell_output += foo.read(1000)
# valid command
foo.write("dir\r")
shell_output += foo.read(1000)
# invalid command
foo.write("asdf\r")
shell_output += foo.read(1000)
# interactive process + tab completion
foo.write("C:\\Python27\\py\t\r")
foo.write("bar = ['baz', 1, True]\r")
foo.write("str(bar)\r")
shell_output += foo.read(1000)
# partial writes
foo.write("pri")
shell_output += foo.read(1000)
foo.write("nt 'hell")
shell_output += foo.read(1000)
foo.write("o'\r")
shell_output += foo.read(1000)

# clean up
foo.write("quit()\r\rexit\r")
shell_output += foo.read(1000)

logging.debug("==================================================================")
logging.debug(shell_output)
logging.debug("==================================================================")

