"""

ConqueSoleCommunicator

Script to transfer communications between python being run in Vim and a
subprocess run inside a Windows console. This is required since interactive
programs in Windows appear to require a console, and python run in Vim is
not attached to any console. So a console version of python must be initiated
for the subprocess. Communication is then done with the use of shared memory
objects. Good times! 

"""

import conque_sole_subprocess, time, mmap, sys
from conque_sole_subprocess import *

import logging # DEBUG
LOG_FILENAME = 'pylog.log' # DEBUG
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG) # DEBUG

##############################################################
# shared memory creation

# size of shared memory
SHM_SIZE = 255

def create_shm (name, access):
    global SHM_SIZE
    name = "%s_%s" % ('conque_sole', name)
    smo = mmap.mmap (0, SHM_SIZE, name, access)
    if not smo:
        exit()
    else:
        return smo

def read_shm (shm):
    global SHM_SIZE
    shm.seek(0)
    shm_str = str(shm.read(SHM_SIZE)).rstrip(chr(0))
    return shm_str

def clear_shm(shm):
    global SHM_SIZE
    shm.seek(0)
    shm.write(chr(0) * SHM_SIZE)

def write_shm(shm, text):
    global SHM_SIZE
    shm.seek(0)
    shm.write(text + chr(0) * (SHM_SIZE - len(text)))

##############################################################
# only run if this file was run directly

if __name__ == '__main__':

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

    ##############################################################
    # Create the subprocess

    proc = ConqueSoleSubprocess()
    res = proc.open(cmd)

    if not res:
        exit()
    
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
                write_shm(output_shm, bucket[:SHM_SIZE])
                bucket = bucket[SHM_SIZE:]

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


