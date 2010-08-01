"""
ConqueSoleSubprocess

Run and communicate with an interactive subprocess in Windows.

Sample Usage:

    sh = ConqueSoleSubprocess()
    sh.open("cmd.exe")
    sh.write("dir\r")
    output = sh.read()
    sh.close()

Requirements:

    * Python for Windows extensions. Available at http://sourceforge.net/projects/pywin32/
    * Must be run from process attached to an existing console.

"""

import time, ctypes, ctypes.wintypes
import win32process, win32console, win32api

import logging # DEBUG
LOG_FILENAME = 'pylog.log' # DEBUG
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG) # DEBUG

class ConqueSoleSubprocess():

    #window = None
    handle = None
    pid = None

    # input / output handles
    stdin = None
    stdout = None

    # max lines for the console buffer
    console_lines = 0
    console_width = 80
    console_height = 24

    # keep track of read position
    current_line = 0
    current_line_text = ''
    lines_look_ahead = 10

    # ****************************************************************************
    # unused as of yet

    def __init__ (self):

        pass

    # ****************************************************************************
    # Create proccess cmd

    def open(self, cmd):

        try:
            # initialize console
            win32console.FreeConsole()
            win32console.AllocConsole()

            # get input / output handles
            self.stdout = win32console.GetStdHandle (win32console.STD_OUTPUT_HANDLE)
            self.stdin = win32console.GetStdHandle (win32console.STD_INPUT_HANDLE)

            # set title
            win32console.SetConsoleTitle ('conquesole process')

            # set console size
            # size = win32console.PyCOORDType (X=1000, Y=30)
            # self.con_stdout.SetConsoleScreenBufferSize (size)

            # get console max lines
            buf_info = self.stdout.GetConsoleScreenBufferInfo()
            self.console_lines = buf_info['Size'].Y - 1
            #self.window = win32console.GetConsoleWindow().handle

            # finally, create the process!
            flags = win32process.NORMAL_PRIORITY_CLASS
            res = win32process.CreateProcess (None, cmd, None, None, 0, flags, None, '.', win32process.STARTUPINFO())
            self.handle = res[0]
            self.pid = res[2]

            return True

        except Exception, e:
            logging.debug('ERROR: %s' % e)
            return False

    # ****************************************************************************
   
    def read(self, timeout = 0):

        output = ""
        read_lines = {}
        changed_lines = []

        # emulate timeout by sleeping timeout time
        if timeout > 0:
            read_timeout = float(timeout) / 1000
            logging.debug("sleep " + str(read_timeout) + " seconds")
            time.sleep(read_timeout)

        # read new data
        for i in range(self.current_line, self.current_line + self.lines_look_ahead + 1):
            logging.debug("reading line " + str(i))
            coord = win32console.PyCOORDType (X=0, Y=i)
            t = self.stdout.ReadConsoleOutputCharacter (Length=self.console_width, ReadCoord=coord)
            logging.debug("line " + str(i) + " is: " + t)
            read_lines[i] = t

            # check if this read reveals new data
            if (i == self.current_line and t != self.current_line_text) or (not t.isspace() and t != ''):
                logging.debug("line " + str(i) + " is different")
                changed_lines.append(i)

        # return now if no new data
        if len(changed_lines) == 0:
            logging.debug("no new data found")
            return ''

        # pull output from current line
        if changed_lines[0] == self.current_line:
            logging.debug("index of first line: " + str(len(self.current_line_text.rstrip())))
            output = read_lines[self.current_line][len(self.current_line_text.rstrip()):].rstrip()
            logging.debug("output from first line: " + output)

        # pull output from additional lines
        if changed_lines[-1] != self.current_line:
            for i in range(self.current_line + 1, changed_lines[-1] + 1):
                output = output + "\n" + read_lines[i].rstrip()
                logging.debug("output from next line: " + read_lines[i].rstrip())

        # reset current line
        self.current_line = changed_lines[-1]
        self.current_line_text = read_lines[changed_lines[-1]]

        logging.debug("full output: " + output)

        return output
        

    # ****************************************************************************

    def write (self, text):
        list_input = []
        for c in text:
            # create keyboard input
            kc = win32console.PyINPUT_RECORDType (win32console.KEY_EVENT)
            kc.Char = unicode(c)
            kc.VirtualKeyCode = ctypes.windll.user32.VkKeyScanA(ord(c))
            kc.KeyDown = True
            kc.RepeatCount = 1

            #if control_key_state:
            #    input_key.ControlKeyState = control_key_state

            list_input.append (kc)

        # write input array
        self.stdin.WriteConsoleInput (list_input)

    # ****************************************************************************

    def close(self):

        win32api.TerminateProcess (self.handle, 0)
        win32api.CloseHandle (self.handle)


