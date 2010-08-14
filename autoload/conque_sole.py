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

import time, re, os, ctypes, ctypes.wintypes
import win32con, win32process, win32console, win32api

import logging # DEBUG
LOG_FILENAME = 'pylog_sub.log' # DEBUG
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG) # DEBUG

# Globals {{{

CONQUE_WINDOWS_VK = {
    '3'  : win32con.VK_CANCEL,
    '8'  : win32con.VK_BACK,
    '9'  : win32con.VK_TAB,
    '12' : win32con.VK_CLEAR,
    '13' : win32con.VK_RETURN,
    '17' : win32con.VK_CONTROL,
    '20' : win32con.VK_CAPITAL,
    '27' : win32con.VK_ESCAPE,
    '28' : win32con.VK_CONVERT,
    '35' : win32con.VK_END,
    '36' : win32con.VK_HOME,
    '37' : win32con.VK_LEFT,
    '38' : win32con.VK_UP,
    '39' : win32con.VK_RIGHT,
    '40' : win32con.VK_DOWN,
    '45' : win32con.VK_INSERT,
    '46' : win32con.VK_DELETE,
    '47' : win32con.VK_HELP
}

CONQUE_SEQ_REGEX_VK = re.compile(ur"(\u001b\[\d{1,3}VK)", re.UNICODE)

CONQUE_ATTRIBUTE_BITS = [ 'fg-blue', 'fg-green', 'fg-red', 'fg-bold', 'bg-blue', 'bg-green', 'bg-red', 'bg-bold' ]

CONQUE_ATTRIBUTE_FOREGROUND = {
    '0000' : '30',
    '0001' : '34',
    '0010' : '32',
    '0011' : '36',
    '0100' : '31',
    '0101' : '35',
    '0110' : '33',
    '0111' : '37',

    '1000' : '1;90',
    '1001' : '1;94',
    '1010' : '1;92',
    '1011' : '1;96',
    '1100' : '1;91',
    '1101' : '1;95',
    '1110' : '1;93',
    '1111' : '1;97'
}

CONQUE_ATTRIBUTE_BACKGROUND = {
    '0000' : '40',
    '0001' : '44',
    '0010' : '42',
    '0011' : '46',
    '0100' : '41',
    '0101' : '45',
    '0110' : '43',
    '0111' : '47',

    '1000' : '1:100',
    '1001' : '1;104',
    '1010' : '1;102',
    '1011' : '1;106',
    '1100' : '1;101',
    '1101' : '1;105',
    '1110' : '1;103',
    '1111' : '1;107'
}

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

    # color stuff
    last_attribute = None

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
            # console window options
            si = win32process.STARTUPINFO()
            si.dwFlags |= win32con.STARTF_USESHOWWINDOW
            #si.wShowWindow = win32con.SW_HIDE
            si.wShowWindow = win32con.SW_MINIMIZE
    
            # process options
            flags = win32process.NORMAL_PRIORITY_CLASS | win32process.CREATE_NEW_PROCESS_GROUP | win32process.CREATE_UNICODE_ENVIRONMENT | win32process.CREATE_NEW_CONSOLE

            # create the process!
            res = win32process.CreateProcess (None, cmd, None, None, 0, flags, None, '.', si)
            self.handle = res[0]
            self.pid = res[2]

            # attach ourselves to the new console
            # console is not immediately available
            for i in range(10):
                time.sleep(1)
                try:
                    logging.debug('attempt ' + str(i))
                    win32console.AttachConsole(self.pid)
                    break
                except Exception, e:
                    logging.debug('ERROR: %s' % e)
                    pass

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

            return True

        except Exception, e:
            logging.debug('ERROR: %s' % e)
            return False

    # }}}

    # ****************************************************************************
   
    def read(self, timeout = 0): # {{{

        output = ""
        read_lines = {}
        text_attributes = {}
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
            a = self.stdout.ReadConsoleOutputAttribute (Length=self.console_width, ReadCoord=coord)
            #logging.debug("line " + str(i) + " is: " + t)
            read_lines[i] = t
            text_attributes[i] = a

        # return now if no new data
        if curs.Y == self.current_line and self.current_line_text == read_lines[self.current_line]:
            #logging.debug("no new data found")
            # always set cursor position
            self.cursor_col = curs.X
            left_esc = ur"\u001b[" + str(self.cursor_col + 1) + "G"
            output += left_esc
            return output

        logging.debug('-----------------------------------------------------------------------')
        logging.debug('current line: ' + self.current_line_text)
        logging.debug('output current line: ' + read_lines[self.current_line])
        logging.debug('output attributes: ' + str(text_attributes[self.current_line]))

        # replace current line
        # check for changes behind cursor
        if self.current_line_text_nice != read_lines[self.current_line][:len(self.current_line_text_nice)]:
            logging.debug("a")
            output = ur"\u001b[2K" + "\r" + ur"\u001b[0m" + self.add_color(read_lines[self.current_line].rstrip(), text_attributes[self.current_line])
        # otherwise append
        else:
            logging.debug("b")
            cut = len(self.current_line_text_nice)
            output = ur"\u001b[" + str(cut + 1) + "G" + self.add_color(read_lines[self.current_line][cut:].rstrip(), text_attributes[self.current_line][cut:])
        logging.debug("output from first line: " + output)
        self.last_attribute = None

        # pull output from additional lines
        if curs.Y > self.current_line:
            for i in range(self.current_line + 1, curs.Y + 1):
                output = output + "\r\n" + self.add_color(read_lines[i].rstrip(), text_attributes[i])
                self.last_attribute = None
                logging.debug("output from next line: " + read_lines[i].rstrip())
                logging.debug("attributes from next line: " + str(text_attributes[i]))

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
            kc.KeyDown = True
            kc.RepeatCount = 1

            cnum = ord(c)

            if cnum > 31:
                kc.Char = unichr(cnum)
                kc.VirtualKeyCode = ctypes.windll.user32.VkKeyScanA(cnum)
            elif cnum == 3:
                pid_list = win32console.GetConsoleProcessList()
                logging.debug(str(self.pid))
                logging.debug(str(pid_list))
                win32console.GenerateConsoleCtrlEvent(win32con.CTRL_C_EVENT, self.pid)
                continue
            else:
                kc.Char = unichr(cnum)
                if str(cnum) in CONQUE_WINDOWS_VK:
                    kc.VirtualKeyCode = CONQUE_WINDOWS_VK[str(cnum)]
                else:
                    kc.VirtualKeyCode = ctypes.windll.user32.VkKeyScanA(cnum + 96)
                    kc.ControlKeyState = win32con.LEFT_CTRL_PRESSED

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

        list_input.append (kc)

        # write input array
        self.stdin.WriteConsoleInput (list_input)

    # }}}

    # ****************************************************************************

    def close(self): # {{{
  
        current_pid = os.getpid()
 
        logging.debug('closing down!')
        pid_list = win32console.GetConsoleProcessList()
        logging.debug(str(self.pid))
        logging.debug(str(pid_list))

        # kill subprocess pids
        for pid in pid_list:        
            # kill current pid last
            if pid == current_pid:
                continue
            try:
                self.close_pid(pid)
            except Exception, e:
                logging.debug('Error closing pid: %s' % e)
                pass

        # kill this process
        try:
            self.close_pid(current_pid)
        except Exception, e:
            logging.debug('Error closing pid: %s' % e)
            pass

    def close_pid (self, pid) :
        logging.debug('killing pid ' + str(pid))
        handle = win32api.OpenProcess(win32con.PROCESS_TERMINATE, 0, pid)
        win32api.TerminateProcess(handle, -1) 
        win32api.CloseHandle(handle)

    # }}}

    # ****************************************************************************
    # add color escape sequences to output

    def add_color(self, text, attributes, start = 0): # {{{

        final_output = ''

        for i in range(start, len(text)):
            final_output += self.attribute_to_escape(attributes[i]) + text[i]

        return final_output

        # }}}

    # ****************************************************************************
    # convert a console attribute integer into an ansi escape sequence

    def attribute_to_escape(self, attr_num): # {{{

        # no change
        if attr_num == self.last_attribute:
            return ''

        self.last_attribute = attr_num

        # if plain white text, use ^[[m
        #if attr_num == 7:
        #    return ur"\u001b[m"

        seq = []

        # convert attribute integer to bit string
        bit_str = bin(attr_num)
        bit_str = bit_str.replace('0b', '')

        # slice foreground and background portions of bit string
        fg = bit_str[-4:].rjust(4, '0')
        bg = bit_str[-8:-4].rjust(4, '0')

        # set escape equivs
        if fg != '' and fg != '0000':
            seq.append(CONQUE_ATTRIBUTE_FOREGROUND[fg])
        if bg != '' and bg != '0000':
            seq.append(CONQUE_ATTRIBUTE_BACKGROUND[bg])

        # clean up
        if len(seq) > 0:
            return ur"\u001b[" + ";".join(seq)  + "m"

        else:
            return ''

        # }}}


    # ****************************************************************************

