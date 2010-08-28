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
import traceback # DEBUG
from ConqueSoleSubprocess import * # DEBUG
from ConqueSoleSharedMemory import * # DEBUG

import logging # DEBUG
LOG_FILENAME = 'pylog_sub.log' # DEBUG
#logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG) # DEBUG

##############################################################
# only run if this file was run directly

if __name__ == '__main__':

    # attempt to catch ALL exceptions to fend of zombies
    try:

        # startup and config {{{

        # simple arg validation
        logging.debug(str(sys.argv))
        if len(sys.argv) < 5:
            logging.debug('Arg validation failed!')
            exit()

        # shared memory size
        CONQUE_SOLE_COMMANDS_SIZE = 255

        # maximum time this thing reads. 0 means no limit. Only for testing.
        max_loops = 0

        # read interval, in seconds
        sleep_time = 0.01

        # idle read interval, in seconds
        idle_sleep_time = 1

        # are we idled?
        is_idle = False

        # mem key
        mem_key = sys.argv[1]

        # console width
        console_width = int(sys.argv[2])

        # console height
        console_height = int(sys.argv[3])

        # the actual subprocess to run
        cmd = " ".join(sys.argv[4:])
        logging.debug('opening command: ' + cmd)

        # width and height
        options = { 'LINES' : console_height, 'COLUMNS' : console_width }

        logging.debug('with options: ' + str(options))

        # }}}

        ##############################################################
        # Create the subprocess

        # {{{
        proc = ConqueSoleSubprocess()
        res = proc.open(cmd, mem_key, options)

        if not res:
            logging.debug('process failed to open')
            exit()

        shm_command = ConqueSoleSharedMemory(CONQUE_SOLE_COMMANDS_SIZE, 'command', mem_key, serialize = True)
        shm_command.create('write')
        shm_command.clear()

        # }}}
        
        ##############################################################
        # main loop!

        loops = 0

        while True:

            # check for idle/resume
            if is_idle or loops % 25 == 0:

                # check process health
                if not proc.is_alive():
                    logging.debug('subprocess appears to be deadish, closing')
                    proc.close()
                    exit()

                # check for change in buffer focus
                cmd = shm_command.read()
                if cmd:
                    if cmd['cmd'] == 'idle':
                        is_idle = True
                        shm_command.clear()
                        logging.debug('idling')
                    elif cmd['cmd'] == 'resume':
                        is_idle = False
                        shm_command.clear()
                        logging.debug('resuming')

            # sleep between loops if moderation is requested
            if sleep_time > 0:
                if is_idle:
                    time.sleep(idle_sleep_time)
                else:
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

    # if an exception was thrown, croak
    except:
        logging.debug(traceback.format_exc())
        proc.close()


