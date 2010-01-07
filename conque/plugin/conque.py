
import vim, sys, os, string, signal, re, time, pty, tty, select, fcntl, termios, struct

import logging # DEBUG
LOG_FILENAME = '/home/nraffo/.vim/pylog.log' # DEBUG
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG) # DEBUG

# CONFIG CONSTANTS  {{{

CONQUE_TERM = 'vt100'

# Escape sequences 
CONQUE_ESCAPE = { 
    'm':'font',
    'J':'clear_screen',
    'K':'clear_line',
    '@':'add_spaces',
    'A':'cursor_up',
    'B':'cursor_down',
    'C':'cursor_right',
    'D':'cursor_left',
    'G':'cursor_to_column',
    'H':'cursor',
    'L':'insert_lines',
    'M':'delete_lines',
    'P':'delete_chars',
    'd':'cusor_vpos',
    'f':'cursor',
    'g':'tab_clear',
    'r':'set_coords',
    'h':'misc_h',
    'l':'misc_l'
}

# Alternate escape sequences, no [
CONQUE_ESCAPE_PLAIN = {
    'D':'scroll_up',
    'E':'next_line',
    'H':'set_tab',
    'M':'scroll_down',
    'N':'single_shift_2',
    'O':'single_shift_3',
    '=':'alternate_keypad',
    '>':'numeric_keypad',
    '7':'save_cursor',
    '8':'restore_cursor'
}

# Uber alternate escape sequences, with # or ?
CONQUE_ESCAPE_QUESTION = {
    '1h':'new_line_mode',
    '3h':'132_cols',
    '4h':'smooth_scrolling',
    '5h':'reverse_video',
    '6h':'relative_origin',
    '7h':'set_auto_wrap',
    '8h':'set_auto_repeat',
    '9h':'set_interlacing_mode',
    '1l':'set_cursor_key',
    '2l':'set_vt52',
    '3l':'80_cols',
    '4l':'set_jump_scrolling',
    '5l':'normal_video',
    '6l':'absolute_origin',
    '7l':'reset_auto_wrap',
    '8l':'reset_auto_repeat',
    '9l':'reset_interlacing_mode'
}

CONQUE_ESCAPE_HASH = {
    '3':'double_height_top',
    '4':'double_height_bottom',
    '5':'single_height_single_width',
    '6':'single_height_double_width',
    '8':'screen_alignment_test'
} 

# regular expression matching (almost) all control sequences
CONQUE_SEQ_REGEX = re.compile(ur"(\u001b\[?\??#?[0-9;]*[a-zA-Z@]|[\u0007-\u000f])", re.DOTALL | re.UNICODE)
CONQUE_SEQ_REGEX_CTL = re.compile(ur"^[\u0007-\u000f]$", re.UNICODE)
CONQUE_SEQ_REGEX_CSI = re.compile(ur"^\u001b\[", re.UNICODE)
CONQUE_SEQ_REGEX_ESC = re.compile(ur"^\u001b", re.UNICODE)

# }}}

###################################################################################################
class Conque:

    # CLASS PROPERTIES {{{ 

    # the buffer
    buffer          = None
    window          = None

    # screen object
    screen          = None

    # subprocess object
    proc            = None

    # terminal dimensions and scrolling region
    columns         = 80 # same as $COLUMNS
    lines           = 24 # same as $LINES
    working_columns = 80 # can be changed by CSI ? 3 l/h
    working_lines   = 24 # can be changed by CSI r

    # top of the scroll region
    top             = 1 # relative to top of screen

    # cursor position
    l               = 1  # current cursor line
    c               = 1  # current cursor column

    # autowrap mode
    autowrap        = True

    # absolute coordinate mode
    absolute_coords = True

    # tabstop positions
    tabstops        = []

    # }}}

    # constructor
    def __init__(self): # {{{
        self.buffer = vim.current.buffer
        self.window = vim.current.window
        self.screen = ConqueScreen()
        # }}}

    # start program and initialize this instance
    def open(self, command): # {{{

        # int vars
        self.columns = self.window.width
        self.lines = self.window.height
        self.working_columns = self.window.width
        self.working_lines = self.window.height

        # init tabstops
        for i in range(1, self.columns):
            if i % 8 == 0:
                self.tabstops.append(True)
            else:
                self.tabstops.append(False)

        # open command
        self.proc = ConqueSubprocess()
        self.proc.open(command)

        # }}}

    # read from pty, and update buffer
    def read(self, timeout = 1): # {{{
        output = self.proc.read(timeout)

        logging.debug('read *********************************************************************')
        logging.debug(str(output))

        debug_profile_start = time.time()
        chunks = CONQUE_SEQ_REGEX.split(output)
        logging.debug('ouput chunking took ' + str((time.time() - debug_profile_start) * 1000) + ' ms')

        debug_profile_start = time.time()
        for s in chunks:
            if s == '':
                continue

            # Check for control character match {{{
            if CONQUE_SEQ_REGEX_CTL.match(s[0]):
                logging.debug(str(s))
                if s == u"\u0007": # bell
                    self.ctl_bel()
                elif s == u"\u0008": # backspace
                    self.ctl_bs()
                elif s == u"\u0009": # tab
                    self.ctl_tab()
                elif s == u"\u000a": # new line
                    self.ctl_nl()
                elif s == u"\u000b": # vertical tab
                    pass
                elif s == u"\u000c": # form feed
                    pass
                elif s == u"\u000d": # carriage return
                    self.ctl_cr()
                elif s == u"\u000e": # shift out
                    pass
                elif s == u"\u000f": # shift in
                    pass
                # }}}

            # check for escape sequence match {{{
            elif CONQUE_SEQ_REGEX_CSI.match(s):
                logging.debug(str(s))
                # }}}
    
            # check for other escape match {{{
            elif CONQUE_SEQ_REGEX_ESC.match(s):
                logging.debug(str(s))
                # }}}
            
            # else process plain text {{{
            else:
                self.plain_text(s)
                # }}}

        #lines = output.split("\n")
        logging.debug('ouput looping took ' + str((time.time() - debug_profile_start) * 1000) + ' ms')

    # }}}

    def test(self):
        self.proc.write("ls -lha\n")
        self.read(500)

    ###############################################################################################
    def plain_text(self, input): # {{{
        current_line = self.screen[self.l]
        if self.c + len(input) > self.working_columns:
            if self.autowrap:
                this_line = input[ : self.working_columns - self.c]
                next_line = input[self.working_columns - self.c + 1 :]
                self.plain_text(this_line)
                self.ctl_nl()
                self.ctl_cr()
                self.plain_text(next_line)
            else:
                self.screen[self.l][self.working_columns] = input[-1]
        else:
            ed_line = current_line[ : self.c - 1] + input
            if len(current_line) > len(ed_line):
                ed_line = ed_line + current_line[ len(ed_line) : ]
            self.screen[self.l] = ed_line
            self.c += len(input)
    # }}}

    ###############################################################################################
    # Control functions {{{

    def ctl_nl(self):
        # if we're in a scrolling region, scroll instead of moving cursor down
        if self.lines != self.working_lines and self.l == self.top + self.working_lines - 1:
            del self.screen[self.top]
            self.screen.insert(self.top + self.working_lines - 1, '')
        else:
            self.l += 1

    def ctl_cr(self):
        self.c = 1

    def ctl_bs(self):
        if self.c > 1:
            self.c += -1

    def ctl_bel(self):
        print 'BELL'

    def ctl_tab(self):
        # default tabstop location
        ts = self.working_columns

        # check set tabstops
        for i in range(self.c, self.working_columns):
            if self.tabstops[i]:
                ts = i
                break

        self.c = ts

    # }}}






