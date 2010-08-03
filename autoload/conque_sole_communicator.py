""" {{{

ConqueSoleCommunicator

Script to transfer communications between python being run in Vim and a
subprocess run inside a Windows console. This is required since interactive
programs in Windows appear to require a console, and python run in Vim is
not attached to any console. So a console version of python must be initiated
for the subprocess. Communication is then done with the use of shared memory
objects. Good times! 

}}} """

import time, mmap, sys
from conque_sole_common import *
from conque_sole_subprocess import *

import logging # DEBUG
LOG_FILENAME = 'pylog_sub.log' # DEBUG
#logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG) # DEBUG

##############################################################
# only run if this file was run directly

if __name__ == '__main__':

    # startup and config {{{

    # simple arg validation
    logging.debug(str(sys.argv))
    if len(sys.argv) < 5:
        logging.debug('Arg validation failed!')
        exit()

    # maximum time this thing reads. 0 means no limit. Only for testing.
    max_loops = 0

    # read interval, in seconds
    sleep_time = 0.01

    # input and output strings, like stdin and stdout
    input_shm = create_shm(sys.argv[1], mmap.ACCESS_WRITE)
    output_shm = create_shm(sys.argv[2], mmap.ACCESS_WRITE)

    # special command string, mostly for sending kill commands
    command_shm = create_shm(sys.argv[3], mmap.ACCESS_WRITE)

    # the actual subprocess to run
    cmd = " ".join(sys.argv[4:])

    # }}}

    ##############################################################
    # Create the subprocess

    # {{{
    proc = ConqueSoleSubprocess()
    res = proc.open(cmd)

    if not res:
        exit()

    # }}}
    
    ##############################################################
    # main loop!

    bucket = ''
    bucket_marker = 0
    loops = 0

    while True:
        #logging.debug('loop...')

        try:
            # check for commands
            cstr = read_shm(command_shm)
            if cstr == 'close':
                try:
                    proc.close()
                except:
                    pass
                exit()

            # write input
            istr = read_shm(input_shm)
            if istr != '':
                #logging.debug('found input: ' + istr)
                # write it to subprocess
                proc.write(istr)
                # clear input when finished
                clear_shm(input_shm)

            # get output from subproccess
            bucket += proc.read()

            #logging.debug("buckit: " + str(bucket))

            # if output shm is empty, add to it
            ostr = read_shm(output_shm)
            if ostr == '':
                #logging.debug('output appears empty, writing: ' + bucket[:SHM_SIZE])
                cut_pos = SHM_SIZE
                # don't cut inside an escape sequence
                if bucket[SHM_SIZE-10:SHM_SIZE].count(chr(27)) > 0:
                    cut_pos = len(bucket[:SHM_SIZE]) - (10 - bucket[SHM_SIZE-10:SHM_SIZE].index(chr(27)))
                write_shm(output_shm, bucket[:cut_pos])
                bucket = bucket[cut_pos:]

        except Exception, e:
            logging.debug('ERROR: %s' % e)

        # sleep between loops if moderation is requested
        if sleep_time > 0:
            time.sleep(sleep_time)

        # increment loops, and exit if max has been reached
        loops += 1
        if max_loops and loops >= max_loops:
            logging.debug('max loops reached')
            exit()


