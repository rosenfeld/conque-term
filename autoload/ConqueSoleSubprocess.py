""" {{{
ConqueSoleSubprocess

Creates a new subprocess with it's own (hidden) console window.

Mirrors console window text onto a block of shared memory (mmap), along with 
text attribute data. Also handles translation of text input into the format
Windows console expects.

Sample Usage:

    sh = ConqueSoleSubprocess()
    sh.open("cmd.exe", "unique_str")

    shm_in = ConqueSoleSharedMemory(mem_key = "unique_str", mem_type = "input", ...)
    shm_out = ConqueSoleSharedMemory(mem_key = "unique_str", mem_type = "output", ...)

    output = shm_out.read(...)
    shm_in.write("dir\r")
    output = shm_out.read(...)

Requirements:

    * Python for Windows extensions. Available at http://sourceforge.net/projects/pywin32/
    * Must be run from process attached to an existing console.

}}} """

import time, re, os, ctypes, ctypes.wintypes, md5, random
import win32con, win32process, win32console, win32api, win32gui, win32event
import traceback # DEBUG
from ConqueSoleSharedMemory import * # DEBUG

import logging # DEBUG
LOG_FILENAME = 'pylog_sub.log' # DEBUG
#logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG) # DEBUG

# Globals {{{

# memory block sizes in characters
CONQUE_SOLE_BUFFER_LENGTH = 1000
CONQUE_SOLE_INPUT_SIZE = 1000
CONQUE_SOLE_STATS_SIZE = 1000
CONQUE_SOLE_COMMANDS_SIZE = 255
CONQUE_SOLE_RESCROLL_SIZE = 255

# interval of full output bucket replacement
# larger number means less frequent, 1 = every time
CONQUE_SOLE_MEM_REDRAW = 1000

# if cursor hasn't moved and screen hasn't scrolled, use this screen redraw interval
# larger number means less frequent, 1 = every time
CONQUE_SOLE_SCREEN_REDRAW = 100

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

# }}}

class ConqueSoleSubprocess():

    # Class properties {{{

    #window = None
    handle = None
    pid = None

    # input / output handles
    stdin = None
    stdout = None

    # size of console window
    window_width = 160
    window_height = 40

    # max lines for the console buffer
    buffer_width = 160
    buffer_height = 100

    # keep track of the buffer number at the top of the window
    top = 0
    line_offset = 0

    # buffer height is CONQUE_SOLE_BUFFER_LENGTH * output_blocks
    output_blocks = 1

    # cursor position
    cursor_line = 0
    cursor_col = 0

    # console data, array of lines
    data = []

    # console attribute data, array of array of int
    attributes = []

    # default attribute
    default_attribute = 7

    # shared memory objects
    shm_input   = None
    shm_output  = None
    shm_attributes = None
    shm_stats   = None
    shm_command = None
    shm_rescroll = None

    # are we still a valid process?
    is_alive = True

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
            try: win32console.FreeConsole()
            except: pass

            # set buffer height
            self.buffer_height = CONQUE_SOLE_BUFFER_LENGTH
            if 'LINES' in options and 'COLUMNS' in options:
                self.window_width  = options['COLUMNS']
                self.window_height = options['LINES']
                self.buffer_width  = options['COLUMNS']

            # console window options
            si = win32process.STARTUPINFO()

            # hide window
            si.dwFlags |= win32con.STARTF_USESHOWWINDOW
            si.wShowWindow = win32con.SW_HIDE
            #si.wShowWindow = win32con.SW_MINIMIZE

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

            # get input / output handles
            self.stdout = win32console.GetStdHandle (win32console.STD_OUTPUT_HANDLE)
            self.stdin = win32console.GetStdHandle (win32console.STD_INPUT_HANDLE)

            # set buffer size
            size = win32console.PyCOORDType (X=self.buffer_width, Y=self.buffer_height)
            self.stdout.SetConsoleScreenBufferSize (size)
            logging.debug('buffer size: ' + str(size))

            # prev set size call needs to process
            time.sleep(0.2)

            # set window size
            self.set_window_size(self.window_width, self.window_height)

            # init shared memory
            self.init_shared_memory(mem_key)

            return True

        except Exception, e:
            logging.debug('ERROR open: %s' % e)
            logging.debug(traceback.format_exc())
            return False

    # }}}

    # ****************************************************************************
    # create shared memory objects
   
    def init_shared_memory(self, mem_key): # {{{

        buf_info = self.stdout.GetConsoleScreenBufferInfo()

        self.shm_input = ConqueSoleSharedMemory(CONQUE_SOLE_INPUT_SIZE, 'input', mem_key)
        self.shm_input.create('write')
        self.shm_input.clear()

        self.shm_output = ConqueSoleSharedMemory(self.buffer_height * self.buffer_width, 'output', mem_key, True)
        self.shm_output.create('write')
        self.shm_output.clear()

        self.shm_attributes = ConqueSoleSharedMemory(self.buffer_height * self.buffer_width, 'attributes', mem_key, True, chr(buf_info['Attributes']))
        self.shm_attributes.create('write')
        self.shm_attributes.clear()

        self.shm_stats = ConqueSoleSharedMemory(CONQUE_SOLE_STATS_SIZE, 'stats', mem_key, serialize = True)
        self.shm_stats.create('write')
        self.shm_stats.clear()

        self.shm_command = ConqueSoleSharedMemory(CONQUE_SOLE_COMMANDS_SIZE, 'command', mem_key, serialize = True)
        self.shm_command.create('write')
        self.shm_command.clear()

        self.shm_rescroll = ConqueSoleSharedMemory(CONQUE_SOLE_RESCROLL_SIZE, 'rescroll', mem_key, serialize = True)
        self.shm_rescroll.create('write')
        self.shm_rescroll.clear()

        return True

    # }}}

    # ****************************************************************************
    # check for and process commands
  
    def check_commands(self): # {{{
 
        cmd = self.shm_command.read()

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

        # no point really
        if not self.is_alive:
            return

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

        # set update range
        if curs_line != self.cursor_line or self.top != buf_info['Window'].Top or random.randint(0, CONQUE_SOLE_SCREEN_REDRAW) == 0:
            read_start = self.top
            read_end   = buf_info['Window'].Bottom + 1
        else:
            read_start = curs_line
            read_end   = curs_line + 1

        # read new data
        for i in range(read_start, read_end):
            #logging.debug("reading line " + str(i))
            coord = win32console.PyCOORDType (X=0, Y=i)
            t = self.stdout.ReadConsoleOutputCharacter (Length=self.buffer_width, ReadCoord=coord)
            a = self.stdout.ReadConsoleOutputAttribute (Length=self.buffer_width, ReadCoord=coord)
            #logging.debug("line " + str(i) + " is: " + t)
            #logging.debug("attributes " + str(i) + " is: " + str(a))

            # add data
            if i >= len(self.data): 
                self.data.append(t)
                self.attributes.append(self.attr_string(a, buf_info))
            else: 
                self.data[i] = t
                self.attributes[i] = self.attr_string(a, buf_info)

        # write new output to shared memory
        if random.randint(0, CONQUE_SOLE_MEM_REDRAW) == CONQUE_SOLE_MEM_REDRAW:
            self.shm_output.write(''.join(self.data))
            self.shm_attributes.write(''.join(self.attributes))
        else:
            self.shm_output.write(text = ''.join(self.data[read_start : read_end]), start = read_start * self.buffer_width)
            self.shm_attributes.write(text = ''.join(self.attributes[read_start : read_end]), start = read_start * self.buffer_width)

        # write cursor position to shared memory
        stats = { 'top_offset' : buf_info['Window'].Top, 'default_attribute' : buf_info['Attributes'], 'cursor_x' : curs_col, 'cursor_y' : curs_line }
        self.shm_stats.write(stats)
        #logging.debug('wtf cursor: ' + str(buf_info))

        # adjust screen position
        self.top = buf_info['Window'].Top
        self.cursor_line = curs_line

        # check for reset
        if self.top > CONQUE_SOLE_BUFFER_LENGTH * self.output_blocks - 50:
            self.reset_console(buf_info)

        return None
        
    # }}}

    # ****************************************************************************
    # clear the console and set cursor at home position

    def reset_console(self, buf_info): # {{{

        self.output_blocks += 1

        # close down old memory
        self.shm_output.close()
        self.shm_output = None

        self.shm_attributes.close()
        self.shm_attributes = None

        # new shared memory key
        mem_key = md5.new(str(self.output_blocks) + str(time.ctime())).hexdigest()[:8]

        # reallocate memory
        self.shm_output = ConqueSoleSharedMemory(self.buffer_height * self.buffer_width * self.output_blocks, 'output', mem_key, True)
        self.shm_output.create('write')
        self.shm_output.clear()
        self.shm_output.write(''.join(self.data))

        self.shm_attributes = ConqueSoleSharedMemory(self.buffer_height * self.buffer_width * self.output_blocks, 'attributes', mem_key, True, chr(buf_info['Attributes']))
        self.shm_attributes.create('write')
        self.shm_attributes.clear()
        self.shm_attributes.write(''.join(self.attributes))

        # notify wrapper of new output block
        self.shm_rescroll.write ({ 'cmd' : 'new_output', 'data' : {'blocks' : self.output_blocks, 'mem_key' : mem_key } })

        # set buffer size
        size = win32console.PyCOORDType (X=self.buffer_width, Y=self.buffer_height * self.output_blocks)
        logging.debug('new buffer size: ' + str(size))
        self.stdout.SetConsoleScreenBufferSize (size)

        # prev set size call needs to process
        time.sleep(0.2)

        # set window size
        self.set_window_size(self.window_width, self.window_height)

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

        logging.debug("\n".join(self.data))
  
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
    # check process health

    def is_alive(self): # {{{

        status = win32event.WaitForSingleObject(self.handle, 1)

        if status == 0:
            self.is_alive = False

        return self.is_alive

        # }}}

    # ****************************************************************************
    # attribute number to one byte character

    def attr_string(self, attr_list, buf_info): # {{{

        s = ''

        for a in attr_list:
            s = s + unichr(a).encode('latin1', chr(buf_info['Attributes']))

        return s

        # }}}

    # ****************************************************************************
    # return screen data as string

    def get_screen_text(self): # {{{

        return "\n".join(self.data)

        # }}}

    # ****************************************************************************

    def set_window_size(self, width, height): # {{{

        # get current window size object
        window_size = self.stdout.GetConsoleScreenBufferInfo()['Window']
        logging.debug('window size: ' + str(window_size))

        # buffer info has maximum window size data
        buf_info = self.stdout.GetConsoleScreenBufferInfo()
        logging.debug(str(buf_info))

        # set top left corner
        window_size.Top  = 0
        window_size.Left = 0

        # set bottom right corner
        if buf_info['MaximumWindowSize'].X < width:
            window_size.Right = buf_info['MaximumWindowSize'].X - 1
        else:
            window_size.Right = width - 1

        if buf_info['MaximumWindowSize'].Y < height:
            window_size.Bottom = buf_info['MaximumWindowSize'].Y - 1
        else:
            window_size.Bottom = height - 1

        logging.debug('window size: ' + str(window_size))

        # set the window size!
        self.stdout.SetConsoleWindowInfo (True, window_size)

        # reread buffer info to get final console max lines
        buf_info = self.stdout.GetConsoleScreenBufferInfo()
        logging.debug('buffer size: ' + str(buf_info))
        self.window_width  = buf_info['Window'].Right + 1
        self.window_height = buf_info['Window'].Bottom + 1

        # }}}


