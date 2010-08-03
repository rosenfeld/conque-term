""" {{{
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

}}} """

import time, re, ctypes, ctypes.wintypes
import win32con, win32process, win32console, win32api

import logging # DEBUG
LOG_FILENAME = 'pylog_sub.log' # DEBUG
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG) # DEBUG

# Globals {{{

CONQUE_WINDOWS_VK = {
    '8'  : win32con.VK_BACK,
    '3'  : win32con.VK_CANCEL,
    '46' : win32con.VK_DELETE,
    '40' : win32con.VK_DOWN,
    '35' : win32con.VK_END,
    '47' : win32con.VK_HELP,
    '36' : win32con.VK_HOME,
    '45' : win32con.VK_INSERT,
    '37' : win32con.VK_LEFT,
    '13' : win32con.VK_RETURN,
    '39' : win32con.VK_RIGHT,
    '38' : win32con.VK_UP
}

CONQUE_SEQ_REGEX_VK = re.compile(ur"(\u001b\[\d{1,3}VK)", re.UNICODE)

# }}}

class ConqueSoleSubprocess():

    # Class properties {{{

    #window = None
    handle = None
    pid = None

    # input / output handles
    stdin = None
    stdout = None

    # max lines for the console buffer
    console_lines = 1000
    console_width = 168
    console_height = 1000

    # keep track of read position
    current_line = 0
    current_line_text = ''
    current_line_text_nice = ''
    lines_look_ahead = 10

    # cursor position
    cursor_line = 0
    cursor_col = 0

    # }}}

    # ****************************************************************************
    # unused as of yet

    def __init__ (self): # {{{

        pass

    # }}}

    # ****************************************************************************
    # Create proccess cmd

    def open(self, cmd): # {{{

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
            size = win32console.PyCOORDType (X=self.console_width, Y=self.console_height)
            self.stdout.SetConsoleScreenBufferSize (size)

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

    # }}}

    # ****************************************************************************
   
    def read(self, timeout = 0): # {{{

        output = ""
        read_lines = {}
        changed_lines = []

        # emulate timeout by sleeping timeout time
        if timeout > 0:
            read_timeout = float(timeout) / 1000
            #logging.debug("sleep " + str(read_timeout) + " seconds")
            time.sleep(read_timeout)

        # get cursor position
        dct_info = self.stdout.GetConsoleScreenBufferInfo()
        curs = dct_info['CursorPosition']

        # check for insane cursor position
        if curs.Y < self.current_line:
            logging.debug('wtf cursor: ' + str(curs))
            self.current_line = curs.Y

        # read new data
        for i in range(self.current_line, curs.Y + 1):
            #logging.debug("reading line " + str(i))
            coord = win32console.PyCOORDType (X=0, Y=i)
            t = self.stdout.ReadConsoleOutputCharacter (Length=self.console_width, ReadCoord=coord)
            #logging.debug("line " + str(i) + " is: " + t)
            read_lines[i] = t

        # return now if no new data
        if curs.Y == self.current_line and self.current_line_text == read_lines[self.current_line]:
            #logging.debug("no new data found")
            # always set cursor position
            self.cursor_col = curs.X
            left_esc = ur"\u001b[" + str(self.cursor_col + 1) + "G"
            output += left_esc
            return output

        logging.debug('-----------------------------------------------------------------------')
        logging.debug('current line: ' + str(self.current_line_text))
        logging.debug('output current line: ' + str(read_lines[self.current_line]))

        # replace current line
        # check for changes behind cursor
        if self.current_line_text_nice != read_lines[self.current_line][:len(self.current_line_text_nice)]:
            logging.debug("a")
            output = ur"\u001b[2K" + "\r" + read_lines[self.current_line].rstrip()
        # otherwise append
        else:
            logging.debug("b")
            cut = len(self.current_line_text_nice)
            output = ur"\u001b[" + str(cut + 1) + "G" + read_lines[self.current_line][cut:].rstrip()
        logging.debug("output from first line: " + output)

        # pull output from additional lines
        if curs.Y > self.current_line:
            for i in range(self.current_line + 1, curs.Y + 1):
                output = output + "\r\n" + read_lines[i].rstrip()
                logging.debug("output from next line: " + read_lines[i].rstrip())

        # reset current line
        self.current_line = curs.Y
        self.current_line_text = read_lines[curs.Y]
        self.current_line_text_nice = read_lines[curs.Y][:curs.X + 1]
        self.cursor_col = curs.X

        # do we need to reset?
        if self.current_line > self.console_lines - 100:
            self.reset_console()

        # always set cursor position
        left_esc = ur"\u001b[" + str(self.cursor_col + 1) + "G"
        logging.debug('left esc: ' + left_esc)
        output += left_esc

        logging.debug("full output: " + output)

        return output
        
    # }}}

    # ****************************************************************************
    # clear the console and set cursor at home position

    def reset_console(self): # {{{

        logging.debug('_______________________________________________________')
        logging.debug('=======================================================')
        logging.debug('-------------------------------------------------------')
        logging.debug('cursor line is ' + str(self.cursor_line))
        logging.debug('cursor col  is ' + str(self.cursor_col))
        logging.debug('current line is ' + str(self.current_line))
        logging.debug('current line text is ' + self.current_line_text)

        # move cusor to home position
        zero = win32console.PyCOORDType (X=0, Y=0)
        self.stdout.SetConsoleCursorPosition (zero)

        # calculate character length of buffer
        dct_info = self.stdout.GetConsoleScreenBufferInfo()
        size = dct_info['Size']
        length = size.X * size.Y

        # fill console with blank char
        self.stdout.FillConsoleOutputCharacter (u' ', length, zero)
        self.stdout.WriteConsole (self.current_line_text)

        # reset current cursor position
        current_pos = win32console.PyCOORDType (X=self.cursor_col, Y=0)
        self.stdout.SetConsoleCursorPosition (current_pos)

        # reset position attributes
        self.cursor_line = 0
        self.current_line = 0

    # }}}

    # ****************************************************************************
    # write text to console. this function just parses out special sequences for
    # special key events and passes on the text to the plain or virtual key functions

    def write (self, text): # {{{

        # split on VK codes
        chunks = CONQUE_SEQ_REGEX_VK.split(text)

        # if len() is one then no vks
        if len(chunks) == 1:
            self.write_plain(text)
            return

        logging.debug('split!: ' + str(chunks))

        # loop over chunks and delegate
        for t in chunks:

            if t == '':
                continue

            if CONQUE_SEQ_REGEX_VK.match(t):
                logging.debug('match!: ' + str(t[2:-2]))
                self.write_vk(t[2:-2])
            else:
                self.write_plain(t)

    # }}}

    # ****************************************************************************

    def write_plain (self, text): # {{{
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

    # }}}

    # ****************************************************************************

    def write_vk (self, vk_code): # {{{
        list_input = []

        # create keyboard input
        kc = win32console.PyINPUT_RECORDType (win32console.KEY_EVENT)
        kc.VirtualKeyCode = CONQUE_WINDOWS_VK[vk_code]
        kc.KeyDown = True
        kc.RepeatCount = 1

        #if control_key_state:
        #    input_key.ControlKeyState = control_key_state

        list_input.append (kc)

        # write input array
        self.stdin.WriteConsoleInput (list_input)

    # }}}

    # ****************************************************************************

    def close(self): # {{{

        win32api.TerminateProcess (self.handle, 0)
        win32api.CloseHandle (self.handle)

    # }}}


