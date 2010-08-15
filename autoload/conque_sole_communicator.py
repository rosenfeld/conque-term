""" {{{

ConqueSoleCommunicator

Script to transfer communications between python being run in Vim and a
subprocess run inside a Windows console. This is required since interactive
programs in Windows appear to require a console, and python run in Vim is
not attached to any console. So a console version of python must be initiated
for the subprocess. Communication is then done with the use of shared memory
objects. Good times! 

}}} """

import time, sys
from ConqueSole import * # DEBUG

import logging # DEBUG
LOG_FILENAME = 'pylog_sub.log' # DEBUG
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG) # DEBUG

##############################################################
# only run if this file was run directly

if __name__ == '__main__':

    # startup and config {{{

    # simple arg validation
    logging.debug(str(sys.argv))
    if len(sys.argv) < 3:
        logging.debug('Arg validation failed!')
        exit()

    # maximum time this thing reads. 0 means no limit. Only for testing.
    max_loops = 100

    # read interval, in seconds
    sleep_time = 0.15

    # the actual subprocess to run
    cmd = " ".join(sys.argv[2:])
    logging.debug('opening command: ' + cmd)

    # width and height
    options = { 'LINES' : 40, 'COLUMNS' : 150 }

    # }}}

    ##############################################################
    # Create the subprocess

    # {{{
    proc = ConqueSole()
    res = proc.open(cmd, sys.argv[1], options)

    if not res:
        logging.debug('process failed to open')
        exit()

    # }}}
    
    ##############################################################
    # main loop!

    loops = 0

    while True:
        #logging.debug('loop...')

        # sleep between loops if moderation is requested
        if sleep_time > 0:
            time.sleep(sleep_time)

        # write, read, etc
        proc.write()
        proc.read()

        # increment loops, and exit if max has been reached
        loops += 1
        if max_loops and loops >= max_loops:
            logging.debug('max loops reached')
            break

    ##############################################################
    # all done!

    logging.debug(proc.get_screen_text())

    proc.close()


