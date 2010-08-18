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

import time, re, os, ctypes, ctypes.wintypes, pickle, md5
import win32con, win32process, win32console, win32api, win32gui
from ConqueSoleSharedMemory import * # DEBUG

import logging # DEBUG
LOG_FILENAME = 'pylog_sub.log' # DEBUG
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG) # DEBUG

# Globals {{{

# shared constants
CONQUE_SOLE_BUFFER_LENGTH = 100
CONQUE_SOLE_INPUT_SIZE = 1000
CONQUE_SOLE_STATS_SIZE = 1000
CONQUE_SOLE_COMMANDS_SIZE = 255

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
    console_width = 160
    console_height = 40

    buffer_cols = 160
    buffer_lines = 100

    # keep track of the buffer number at the top of the window
    top = 0
    line_offset = 0
    output_blocks = 1

    # cursor position
    cursor_line = 0
    cursor_col = 0

    # console data, array of lines
    data = []

    # console attribute data, array of array of int
    attributes = []

    # shared memory objects
    shm_input   = None
    shm_output  = None
    shm_attributes = None
    shm_stats   = None
    shm_command = None

    # }}}

    # ****************************************************************************
    # initialize class instance

    def __init__ (self): # {{{

        pass

    # }}}

    # ****************************************************************************
    # Create proccess cmd

    def open(self, cmd, mem_key, options = {}): # {{{

        self.reset = True

        try:
            # if we're already attached to a console, then unattach
            try:
                win32console.FreeConsole()
            except:
                pass

            # set width and height properties
            self.buffer_lines = CONQUE_SOLE_BUFFER_LENGTH
            if 'LINES' in options and 'COLUMNS' in options:
                self.console_width  = options['COLUMNS']
                self.console_height = options['LINES']

            # console window options
            si = win32process.STARTUPINFO()

            # hide window
            si.dwFlags |= win32con.STARTF_USESHOWWINDOW
            #si.wShowWindow = win32con.SW_HIDE
            si.wShowWindow = win32con.SW_MINIMIZE

            # window size
            si.dwFlags |= win32con.STARTF_USECOUNTCHARS
            si.dwXCountChars = self.console_width
            si.dwYCountChars = self.console_height
    
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
                    logging.debug('ERROR attach: %s' % e)
                    pass

            # get window handle
            self.window = win32console.GetConsoleWindow()
            #win32gui.SetWindowPos(self.window, None, 0, 0, self.console_width, self.console_height, None)

            # get input / output handles
            self.stdout = win32console.GetStdHandle (win32console.STD_OUTPUT_HANDLE)
            self.stdin = win32console.GetStdHandle (win32console.STD_INPUT_HANDLE)

            # set title
            win32console.SetConsoleTitle ('conquesole process')

            # set buffer size
            size = win32console.PyCOORDType (X=self.console_width, Y=self.buffer_lines)
            self.stdout.SetConsoleScreenBufferSize (size)

            # prev set size call needs to process
            time.sleep(0.2)

            # set window size
            window_size = self.stdout.GetConsoleScreenBufferInfo()['Window']
            logging.debug('window size: ' + str(window_size))
            window_size.Top = 0
            window_size.Left = 0
            window_size.Right = self.console_width - 1
            window_size.Bottom = self.console_height
            logging.debug('window size: ' + str(window_size))
            self.stdout.SetConsoleWindowInfo (True, window_size)

            # reread buffer info to get final console max lines
            buf_info = self.stdout.GetConsoleScreenBufferInfo()
            self.buffer_lines = buf_info['Size'].Y
            self.buffer_cols = buf_info['Size'].X
            logging.debug('buffer size: ' + str(buf_info))


            # sanity check
            if self.buffer_lines * self.buffer_cols > 1000000 or self.buffer_lines * self.buffer_cols < 100:
                print "Error: screen size appears excessive. (" + str(self.buffer_lines) + " x " + str(self.buffer_cols) + ")"
                self.close()
                return false

            # init shared memory
            self.init_shared_memory(mem_key)

            return True

        except Exception, e:
            logging.debug('ERROR open: %s' % e)
            return False

    # }}}

    # ****************************************************************************
    # create shared memory objects
   
    def init_shared_memory(self, mem_key): # {{{

        self.shm_input = ConqueSoleSharedMemory(CONQUE_SOLE_INPUT_SIZE, 'input', mem_key)
        self.shm_input.create('write')
        self.shm_input.clear()

        self.shm_output = ConqueSoleSharedMemory(self.buffer_lines * self.buffer_cols, 'output', mem_key, True)
        self.shm_output.create('write')
        self.shm_output.clear()

        self.shm_stats = ConqueSoleSharedMemory(CONQUE_SOLE_STATS_SIZE, 'stats', mem_key)
        self.shm_stats.create('write')
        self.shm_stats.clear()

        self.shm_command = ConqueSoleSharedMemory(CONQUE_SOLE_COMMANDS_SIZE, 'command', mem_key)
        self.shm_command.create('write')
        self.shm_command.clear()

        return True

    # }}}

    # ****************************************************************************
    # check for and process commands
  
    def check_commands(self): # {{{
 
        cmd_str = self.shm_command.read()

        if cmd_str == '':
            return

        cmd = pickle.loads(cmd_str)

        if not cmd or cmd == '':
            return

        # shut it all down
        if cmd['cmd'] == 'close':
            self.close()
            return

        # }}}

    # ****************************************************************************
    # read from windows console and update output buffer
   
    def read(self, timeout = 0): # {{{

        # check for commands
        self.check_commands()

        # emulate timeout by sleeping timeout time
        if timeout > 0:
            read_timeout = float(timeout) / 1000
            #logging.debug("sleep " + str(read_timeout) + " seconds")
            time.sleep(read_timeout)

        # get cursor position
        buf_info = self.stdout.GetConsoleScreenBufferInfo()
        curs_line = buf_info['CursorPosition'].Y
        curs_col = buf_info['CursorPosition'].X

        # read new data
        for i in range(self.top, buf_info['Window'].Bottom + 1):
            #logging.debug("reading line " + str(i))
            coord = win32console.PyCOORDType (X=0, Y=i)
            t = self.stdout.ReadConsoleOutputCharacter (Length=self.console_width, ReadCoord=coord)
            a = self.stdout.ReadConsoleOutputAttribute (Length=self.console_width, ReadCoord=coord)
            #logging.debug("line " + str(i) + " is: " + t)

            # add data
            if i + self.line_offset >= len(self.data): 
                self.data.append(t)
            else: 
                self.data[i + self.line_offset] = t

            # and character attributes
            if i + self.line_offset >= len(self.attributes): self.attributes.append(a)
            else:                         self.attributes[i + self.line_offset] = a

        # write new output to shared memory
        self.shm_output.write(text = ''.join(self.data[self.top + self.line_offset : buf_info['Window'].Bottom + 1 + self.line_offset]), start = self.top * self.buffer_cols + self.line_offset * self.buffer_cols)

        # write cursor position to shared memory
        stats = { 'top_offset' : buf_info['Window'].Top + self.line_offset, 'cursor_x' : curs_col, 'cursor_y' : curs_line + self.line_offset }
        self.shm_stats.write(pickle.dumps(stats, 0))
        #logging.debug('wtf cursor: ' + str(buf_info))

        # adjust screen position
        self.top = buf_info['Window'].Top

        #logging.debug("full output: " + ''.join(self.data[self.top : curs_line + 1]))

        # check for reset
        self.reset_console()

        return None
        
    # }}}

    # ****************************************************************************
    # clear the console and set cursor at home position

    def reset_console(self): # {{{

        # most of the time, do nothing
        if self.top < CONQUE_SOLE_BUFFER_LENGTH - 50:
            return

        # calculate character length of buffer
        buf_info = self.stdout.GetConsoleScreenBufferInfo()
        size = buf_info['Size']
        length = size.X * size.Y

        logging.debug('a')

        self.output_blocks += 1
        self.line_offset += buf_info['Window'].Top

        logging.debug('b')
        # close down old memory
        self.shm_output.close()
        self.shm_output = None

        logging.debug('a')
        # reallocate memory
        mem_key = md5.new(str(self.output_blocks) + str(time.ctime())).hexdigest()[:8]
        logging.debug(str(self.buffer_lines))
        logging.debug( str(self.buffer_cols ))
        logging.debug( str(self.output_blocks))
        logging.debug(str(self.buffer_lines * self.buffer_cols * self.output_blocks))
        self.shm_output = ConqueSoleSharedMemory(self.buffer_lines * self.buffer_cols * self.output_blocks, 'output', mem_key, True)
        logging.debug('c')
        self.shm_output.create('write')
        logging.debug('a')
        self.shm_output.clear()
        logging.debug('d')
        self.shm_output.write(''.join(self.data))

        logging.debug('a')
        # notify wrapper of new output block
        self.shm_command.write(pickle.dumps({'cmd' : 'new_output', 'data' : {'blocks' : self.output_blocks, 'mem_key' : mem_key } }))

        logging.debug('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaiiii')

        # move cusor to home position
        zero = win32console.PyCOORDType (X=0, Y=0)
        self.stdout.SetConsoleCursorPosition (zero)

        logging.debug('a')

        # fill console with blank char
        self.stdout.FillConsoleOutputCharacter (u' ', length, zero)
        logging.debug('b')

        # then refill with data
        self.stdout.WriteConsoleOutputCharacter ("".join(self.data[self.top:]), zero)
        self.data = self.data[self.top:]

        logging.debug('c')
        # reset current cursor position
        current = win32console.PyCOORDType (X=buf_info['CursorPosition'].X, Y=buf_info['CursorPosition'].Y-self.top)
        self.stdout.SetConsoleCursorPosition (current)

        logging.debug('d')
        # reset line number of top of screen
        self.top = 0


    # }}}

    # ****************************************************************************
    # write text to console. this function just parses out special sequences for
    # special key events and passes on the text to the plain or virtual key functions

    def write (self): # {{{

        # get input from shared mem
        text = self.shm_input.read()

        # nothing to do here
        if text == '':
            return

        logging.debug('writing: ' + text)

        # clear input queue
        self.shm_input.clear()

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
    # return screen data as string

    def get_screen_text(self):
        logging.debug('here')
        logging.debug(str(len(self.data)))
        return "\n".join(self.data)


