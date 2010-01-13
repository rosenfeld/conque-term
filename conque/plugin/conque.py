
import vim, sys, os, string, signal, re, time, pty, tty, select, fcntl, termios, struct

import logging # DEBUG
LOG_FILENAME = '/home/nraffo/.vim/pylog.log' # DEBUG
#logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG) # DEBUG

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
    'P':'delete_chars',
    'f':'cursor',
    'g':'tab_clear',
    'r':'set_coords',
    'h':'set',
    'l':'reset'
}
#    'L':'insert_lines',
#    'M':'delete_lines',
#    'd':'cusor_vpos',

# Alternate escape sequences, no [
CONQUE_ESCAPE_PLAIN = {
    'D':'scroll_up',
    'E':'next_line',
    'H':'set_tab',
    'M':'scroll_down'
}
#    'N':'single_shift_2',
#    'O':'single_shift_3',
#    '=':'alternate_keypad',
#    '>':'numeric_keypad',
#    '7':'save_cursor',
#    '8':'restore_cursor',

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
    '8':'screen_alignment_test'
} 
#    '3':'double_height_top',
#    '4':'double_height_bottom',
#    '5':'single_height_single_width',
#    '6':'single_height_double_width',

# regular expression matching (almost) all control sequences
CONQUE_SEQ_REGEX      = re.compile(ur"(\u001b\[?\??#?[0-9;]*[a-zA-Z@]|[\u0007-\u000f])", re.UNICODE)
CONQUE_SEQ_REGEX_CTL  = re.compile(ur"^[\u0007-\u000f]$", re.UNICODE)
CONQUE_SEQ_REGEX_CSI  = re.compile(ur"^\u001b\[", re.UNICODE)
CONQUE_SEQ_REGEX_HASH = re.compile(ur"^\u001b#", re.UNICODE)
CONQUE_SEQ_REGEX_ESC  = re.compile(ur"^\u001b", re.UNICODE)

# match table output
CONQUE_TABLE_OUTPUT   = re.compile("^\s*\|\s.*\s\|\s*$|^\s*\+[=+-]+\+\s*$")

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

    # top/bottom of the scroll region
    top             = 1  # relative to top of screen
    bottom          = 24 # relative to top of screen

    # cursor position
    l               = 1  # current cursor line
    c               = 1  # current cursor column

    # autowrap mode
    autowrap        = True

    # absolute coordinate mode
    absolute_coords = True

    # tabstop positions
    tabstops        = []

    # color changes
    color_changes = []

    # function dictionaries
    csi_functions = {}
    esc_functions = {}
    hash_functions = {}

    # don't wrap table output
    table_output = True

    # }}}

    # constructor
    def __init__(self): # {{{
        self.buffer = vim.current.buffer
        self.window = vim.current.window
        self.screen = ConqueScreen()

        # initialize function mappings
        for k in CONQUE_ESCAPE.keys():
            self.csi_functions[k] = getattr(self, 'csi_' + CONQUE_ESCAPE[k])

        for k in CONQUE_ESCAPE_PLAIN.keys():
            self.esc_functions[k] = getattr(self, 'esc_' + CONQUE_ESCAPE_PLAIN[k])

        for k in CONQUE_ESCAPE_HASH.keys():
            self.hash_functions[k] = getattr(self, 'hash_' + CONQUE_ESCAPE_HASH[k])
        # }}}

    # start program and initialize this instance
    def open(self, command): # {{{

        # int vars
        self.columns = self.window.width
        self.lines = self.window.height
        self.working_columns = self.window.width
        self.working_lines = self.window.height
        self.bottom = self.window.height

        # init tabstops
        for i in range(0, self.columns + 1):
            if i % 8 == 0:
                self.tabstops.append(True)
            else:
                self.tabstops.append(False)

        # open command
        self.proc = ConqueSubprocess()
        self.proc.open(command, { 'TERM' : CONQUE_TERM, 'CONQUE' : '1', 'LINES' : str(self.lines), 'COLUMNS' : str(self.columns)})
        # }}}

    # read from pty, and update buffer
    def read(self, timeout = 1): # {{{
        output = self.proc.read(timeout)

        if output == '':
            return

        logging.debug('read *********************************************************************')
        logging.debug(str(output))
        debug_profile_start = time.time()

        chunks = CONQUE_SEQ_REGEX.split(output)
        logging.debug('ouput chunking took ' + str((time.time() - debug_profile_start) * 1000) + ' ms')

        debug_profile_start = time.time()
        for s in chunks:
            if s == '':
                continue

            logging.debug(str(s) + '--------------------------------------------------------------')
            logging.debug('at line ' + str(self.l) + ' column ' + str(self.c))
            logging.debug('current: ' + self.screen[self.l])

            # Check for control character match {{{
            if CONQUE_SEQ_REGEX_CTL.match(s[0]):
                logging.debug('control match')
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
                logging.debug('csi match')
                if s[-1] in self.csi_functions:
                    csi = self.parse_csi(s[2:])
                    logging.debug(str(csi))
                    self.csi_functions[s[-1]](csi)
                else:
                    logging.debug('escape not found for ' + str(s))
                # }}}
    
            # check for hash match {{{
            elif CONQUE_SEQ_REGEX_HASH.match(s):
                logging.debug('hash match')
                if s[-1] in self.hash_functions:
                    csi = self.parse_csi(s[2:])
                    self.hash_functions[s[-1]](csi)
                else:
                    logging.debug('escape not found for ' + str(s))
                # }}}
            
            # check for other escape match {{{
            elif CONQUE_SEQ_REGEX_ESC.match(s):
                logging.debug('escape match')
                if s[-1] in self.esc_functions:
                    csi = self.parse_csi(s[1:])
                    self.esc_functions[s[-1]](csi)
                else:
                    logging.debug('escape not found for ' + str(s))
                # }}}
            
            # else process plain text {{{
            else:
                self.plain_text(s)
                # }}}

        # set cursor position
        self.screen.set_cursor(self.l, self.c)

        vim.command('redraw')

        logging.info('::: read took ' + str((time.time() - debug_profile_start) * 1000) + ' ms')
    # }}}

    def auto_read(self): # {{{
        self.read(1)
        vim.command('call feedkeys("\<F7>", "t")')
        self.screen.set_cursor(self.l, self.c)
    # }}}

    def write(self, input): # {{{
        logging.debug('writing input ' + str(input))

        # write and read
        self.proc.write(input)
        self.read(1)
        # }}}

    ###############################################################################################
    def plain_text(self, input): # {{{
        current_line = self.screen[self.l]

        if len(current_line) < self.working_columns:
            current_line = current_line + ' ' * (self.c - len(current_line))

        # if line is wider than screen
        if self.c + len(input) - 1 > self.working_columns:
            # Table formatting hack
            if self.table_output and CONQUE_TABLE_OUTPUT.match(input):
                self.screen[self.l] = current_line[ : self.c - 1] + input + current_line[ self.c + len(input) - 1 : ]
                self.c += len(input)
                return
            logging.debug('autowrap triggered')
            diff = self.c + len(input) - self.working_columns - 1
            # if autowrap is enabled
            if self.autowrap:
                self.screen[self.l] = current_line[ : self.c - 1] + input[ : -1 * diff ]
                self.ctl_nl()
                self.ctl_cr()
                self.plain_text(input[ -1 * diff : ])
            else:
                self.screen[self.l] = current_line[ : self.c - 1] + input[ : -1 * diff - 1 ] + input[-1]
                self.c = self.working_columns

        # no autowrap
        else:
            self.screen[self.l] = current_line[ : self.c - 1] + input + current_line[ self.c + len(input) - 1 : ]
            self.c += len(input)
    # }}}

    ###############################################################################################
    # Control functions {{{

    def ctl_nl(self):
        # if we're in a scrolling region, scroll instead of moving cursor down
        if self.lines != self.working_lines and self.l == self.bottom:
            del self.screen[self.top]
            self.screen.insert(self.bottom, '')
        elif self.l == self.bottom:
            self.screen.append('')
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

    ###############################################################################################
    # CSI functions {{{

    def csi_font(self, csi): # {{{
        return
        if self.color_changes.len() > 0:
            self.color_changes[-1].end = self.c
        self.color_changes.append({'col': self.c, 'end' : -1 , 'codes': csi['vals']})
        # }}}

    def csi_clear_line(self, csi): # {{{
        logging.debug(str(csi))

        # this escape defaults to 0
        if len(csi['vals']) == 0:
            csi['val'] = 0

        logging.debug('clear line with ' + str(csi['val']))
        logging.debug('original line: ' + self.screen[self.l])

        # 0 means cursor right
        if csi['val'] == 0:
            self.screen[self.l] = self.screen[self.l][0 : self.c - 1]

        # 1 means cursor left
        elif csi['val'] == 1:
            self.screen[self.l] = ' ' * (self.c) + self.screen[self.l][self.c : ]

        # clear entire line
        elif csi['val'] == 2:
            self.screen[self.l] = ''

        logging.debug('new line: ' + self.screen[self.l])
        # }}}

    def csi_cursor_right(self, csi): # {{{
        # we use 1 even if escape explicitly specifies 0
        if csi['val'] == 0:
            csi['val'] = 1

        self.c = self.bound(self.c + csi['val'], 1, self.working_columns)
        # }}}

    def csi_cursor_left(self, csi): # {{{
        # we use 1 even if escape explicitly specifies 0
        if csi['val'] == 0:
            csi['val'] = 1

        self.c = self.bound(self.c - csi['val'], 1, self.working_columns)
        # }}}

    def csi_cursor_to_column(self, csi): # {{{
        self.c = self.bound(csi['val'], 1, self.working_columns)
        # }}}

    def csi_cursor_up(self, csi): # {{{
        self.l = self.bound(self.l - csi['val'], self.top, self.bottom)
        # }}}

    def csi_cursor_down(self, csi): # {{{
        self.l = self.bound(self.l + csi['val'], self.top, self.bottom)
        # }}}

    def csi_clear_screen(self, csi): # {{{
        # default to 0
        if len(csi['vals']) == 0:
            csi['val'] = 0

        # 2 == clear entire screen
        if csi['val'] == 2:
            self.l = 1
            self.c = 1
            self.screen.clear()

        # 0 == clear down
        elif csi['val'] == 0:
            for l in range(self.bound(self.l + 1, 1, self.lines), self.lines + 1):
                self.screen[l] = ''
            
            # clear end of current line
            self.csi_clear_line(self.parse_csi('K'))

        # 1 == clear up
        elif csi['val'] == 1:
            for l in range(1, self.bound(self.l, 1, self.lines + 1)):
                self.screen[l] = ''

            # clear beginning of current line
            self.csi_clear_line(self.parse_csi('1K'))
        # }}}

    def csi_delete_chars(self, csi): # {{{
        self.screen[self.l] = self.screen[self.l][ : self.c ] + self.screen[self.l][ self.c + csi['val'] : ]
        # }}}

    def csi_add_spaces(self, csi): # {{{
        self.screen[self.l] = self.screen[self.l][ : self.c - 1] + ' ' * csi['val'] + self.screen[self.l][self.c : ]
        # }}}

    def csi_cursor(self, csi): # {{{
        if len(csi['vals']) == 2:
            new_line = csi['vals'][0]
            new_col = csi['vals'][1]
        else:
            new_line = 1
            new_col = 1

        if self.absolute_coords:
            self.l = self.bound(new_line, 1, self.lines)
        else:
            self.l = self.bound(self.top + new_line - 1, self.top, self.bottom)

        self.c = self.bound(new_col, 1, self.working_columns)
        if self.c > len(self.screen[self.l]):
            self.screen[self.l] = self.screen[self.l] + ' ' * (self.c - len(self.screen[self.l]))
        # }}}

    def csi_set_coords(self, csi): # {{{
        if len(csi['vals']) == 2:
            new_start = csi['vals'][0]
            new_end = csi['vals'][1]
        else:
            new_start = 1
            new_end = self.window.height

        self.top = new_start
        self.bottom = new_end
        self.working_lines = new_end - new_start + 1
        # }}}

    def csi_tab_clear(self, csi): # {{{
        # this escape defaults to 0
        if len(csi['vals']) == 0:
            csi['val'] = 0

        if csi['val'] == 0:
            self.tabstops[self.c] = False
        elif csi['val'] == 3:
            for i in range(1, self.columns):
                self.tabstops[i] = False
        # }}}

    def csi_set(self, csi): # {{{
        # 132 cols
        if csi['val'] == 3: 
            self.csi_clear_screen(self.parse_csi('2J'))
            self.working_columns = 132

        # relative_origin
        elif csi['val'] == 6: 
            self.absolute_coords = False

        # set auto wrap
        elif csi['val'] == 7: 
            self.autowrap = True

        # }}}

    def csi_reset(self, csi): # {{{
        # 80 cols
        if csi['val'] == 3: 
            self.csi_clear_screen(self.parse_csi('2J'))
            self.working_columns = 80

        # absolute origin
        elif csi['val'] == 6: 
            self.absolute_coords = True

        # reset auto wrap
        elif csi['val'] == 7: 
            self.autowrap = False

        # }}}

    # }}}

    ###############################################################################################
    # ESC functions {{{

    def esc_scroll_up(self, csi): # {{{
        self.ctl_nl()
        # }}}

    def esc_next_line(self, csi): # {{{
        self.ctl_nl()
        self.c = 1
        # }}}

    def esc_set_tab(self, csi): # {{{
        self.tabstops[self.c] = True
        # }}}

    def esc_scroll_down(self, csi): # {{{
        if self.l == self.top:
            del self.screen[self.bottom]
            self.screen.insert(self.top, '')
        else:
            self.l += -1
        # }}}

    # }}}

    ###############################################################################################
    # HASH functions {{{

    def hash_screen_alignment_test(self, csi): # {{{
        self.csi_clear_screen(self.parse_csi('2J'))
        self.working_lines = self.lines
        for l in range(1, self.lines + 1):
            self.screen[l] = 'E' * self.working_columns
        # }}}

    # }}}

    ###############################################################################################
    # Utility {{{
    
    def parse_csi(self, s): # {{{
        attr = { 'key' : s[-1], 'flag' : '', 'val' : 1, 'vals' : [] }

        if len(s) == 1:
            return attr

        full = s[0:-1]

        if full[0] == '?':
            full = full[1:]
            attr['flag'] = '?'

        if full != '':
            vals = full.split(';')
            for val in vals:
                attr['vals'].append(int(val.replace("^0*", "")))

        if len(attr['vals']) == 1:
            attr['val'] = int(attr['vals'][0])
            
        return attr
        # }}}

    def bound(self, val, min, max): # {{{
        if val > max:
            return max

        if val < min:
            return min

        return val
        # }}}

    # }}}

