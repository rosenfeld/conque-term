"""

ConqueSoleSubprocessWrapper

Subprocess wrapper to deal with Windows insanity. Launches console based python, 
which in turn launches originally requested command. Communicates with cosole
python through shared memory objects.

"""

import md5, time, mmap 
import os, sys, time, mmap, struct, ctypes, ctypes.wintypes, logging, tempfile, threading
import win32api, win32con, win32event, win32process, win32console
user32 = ctypes.windll.user32

import logging # DEBUG
LOG_FILENAME = 'pylog.log' # DEBUG
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG) # DEBUG

class ConqueSoleSubprocessWrapper():

    SHM_SIZE = 255
    shm_key = ''

    # process info
    handle = None
    pid = None

    # queue input in this bucket
    bucket = ''

    # shared memory objects
    input_shm = None
    output_shm = None
    command_shm = None

    # console python process
    proc = None

    # path to python exe
    python_exe = 'C:\Python27\python.exe'

    # path to communicator
    communicator_py = 'conque_sole_communicator.py'

    def __init__(self):
        pass

    #########################################################################
    # run communicator process which will in turn run cmd

    def open(self, cmd, options = {}):

        # create a shm key
        self.shm_key = md5.new(cmd + str(time.ctime())).hexdigest()[:8]

        # create shared memory instances
        self.input_shm = self.create_shm('input', mmap.ACCESS_WRITE)
        self.output_shm = self.create_shm('output', mmap.ACCESS_WRITE)
        self.command_shm = self.create_shm('command', mmap.ACCESS_WRITE)

        # python command
        cmd_line = '%s "%s" %s_input %s_output %s_command %s' % (self.python_exe, self.communicator_py, self.shm_key, self.shm_key, self.shm_key, cmd)
        logging.debug('python command: ' + cmd_line)

        # console window attributes
        flags = win32process.NORMAL_PRIORITY_CLASS
        si = win32process.STARTUPINFO()
        si.dwFlags |= win32con.STARTF_USESHOWWINDOW
        # showing minimized window is useful for debugging
        si.wShowWindow = win32con.SW_HIDE
        #si.wShowWindow = win32con.SW_MINIMIZE

        # start the stupid process already
        try:
            tpl_result = win32process.CreateProcess (None, cmd_line, None, None, 0, flags, None, '.', si)
        except:
            logging.debug('COULD NOT START %s' % cmd_line)
            raise

        # handle
        self.handle = tpl_result [0]
        self.pid = tpl_result [2]

    #########################################################################
    # read output from shared memory

    def read(self, timeout = 0):

        # emulate timeout by sleeping timeout time
        if timeout > 0:
            read_timeout = float(timeout) / 1000
            logging.debug("sleep " + str(read_timeout) + " seconds")
            time.sleep(read_timeout)

        # get output
        output = read_shm(self.output_shm)

        # clear output shm
        clear_shm(self.output_shm)

        return output

    #########################################################################
    # write input to shared memory

    def write(self, text):

        self.bucket += text

        logging.debug('writing input: ' + text)
        logging.debug('bucket is now: ' + text)

        istr = read_shm(self.input_shm)
        if istr == '':
            logging.debug('input shm is empty, writing')
            write_shm(self.input_shm, self.bucket[:self.SHM_SIZE])
            self.bucket = self.bucket[self.SHM_SIZE:]

    #########################################################################
    # shut it all down

    def close(self):
        write_shm(self.command_shm, 'close')
        time.sleep(0.2)
        #win32api.TerminateProcess (self.handle, 0)
        #win32api.CloseHandle (self.handle)


    #########################################################################
    # create shared memory instance

    def create_shm (self, name, access):
        name = "%s_%s_%s" % ('conque_sole', self.shm_key, name)
        smo = mmap.mmap (0, self.SHM_SIZE, name, access)
        if not smo:
            return None
        else:
            return smo


#############################################################################
#############################################################################

SHM_SIZE = 255

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

