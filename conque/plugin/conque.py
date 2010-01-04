
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
CONQUE_SEQ_REGEX_SIMPLE = re.compile(ur"^[\u0007-\u001e]", re.UNICODE)

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

    # cursor position
    l               = 1  # current cursor line
    c               = 1  # current cursor column

    # autowrap mode
    autowrap        = 1

    # absolute coordinate mode
    absolute_coords = 1

    # tabstop positions
    tabstops        = {}

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
        for i in range(8, self.columns):
            if i % 8 == 0:
                self.tabstops[i] = 1

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

            if CONQUE_SEQ_REGEX_SIMPLE.match(s[0]):
                pass
                #logging.debug(str(s))
            else:
                self.screen.append(s)

        #lines = output.split("\n")
        logging.debug('ouput looping took ' + str((time.time() - debug_profile_start) * 1000) + ' ms')

    # }}}

    def test(self):
        self.proc.write("ls -lha\n")
        self.read(500)


