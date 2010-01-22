
import vim, re, time, math

import logging # DEBUG
LOG_FILENAME = '/home/nraffo/.vim/pylog.log' # DEBUG
#logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG) # DEBUG

# CONFIG CONSTANTS  {{{

CONQUE_TERM = 'vt100'

CONQUE_CTL = {
     7:'bel', # bell
     8:'bs',  # backspace
     9:'tab', # tab
    10:'nl',  # new line
    13:'cr'   # carriage return
}
#    11 : 'vt',  # vertical tab
#    12 : 'ff',  # form feed
#    14 : 'so',  # shift out
#    15 : 'si'   # shift in

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

# Font codes {{{
CONQUE_FONT = {
    0: {'description':'Normal (default)', 'attributes': {'cterm':'NONE','ctermfg':'NONE','ctermbg':'NONE','gui':'NONE','guifg':'NONE','guibg':'NONE'}, 'normal':True},
    1: {'description':'Bold', 'attributes': {'cterm':'BOLD','gui':'BOLD'}, 'normal':False},
    4: {'description':'Underlined', 'attributes': {'cterm':'UNDERLINE','gui':'UNDERLINE'}, 'normal':False},
    5: {'description':'Blink (appears as Bold)', 'attributes': {'cterm':'BOLD','gui':'BOLD'}, 'normal':False},
    7: {'description':'Inverse', 'attributes': {'cterm':'REVERSE','gui':'REVERSE'}, 'normal':False},
    8: {'description':'Invisible (hidden)', 'attributes': {'ctermfg':'0','ctermbg':'0','guifg':'#000000','guibg':'#000000'}, 'normal':False},
    22: {'description':'Normal (neither bold nor faint)', 'attributes': {'cterm':'NONE','gui':'NONE'}, 'normal':True},
    24: {'description':'Not underlined', 'attributes': {'cterm':'NONE','gui':'NONE'}, 'normal':True},
    25: {'description':'Steady (not blinking)', 'attributes': {'cterm':'NONE','gui':'NONE'}, 'normal':True},
    27: {'description':'Positive (not inverse)', 'attributes': {'cterm':'NONE','gui':'NONE'}, 'normal':True},
    28: {'description':'Visible (not hidden)', 'attributes': {'ctermfg':'NONE','ctermbg':'NONE','guifg':'NONE','guibg':'NONE'}, 'normal':True},
    30: {'description':'Set foreground color to Black', 'attributes': {'ctermfg':'16','guifg':'#000000'}, 'normal':False},
    31: {'description':'Set foreground color to Red', 'attributes': {'ctermfg':'1','guifg':'#ff0000'}, 'normal':False},
    32: {'description':'Set foreground color to Green', 'attributes': {'ctermfg':'2','guifg':'#00ff00'}, 'normal':False},
    33: {'description':'Set foreground color to Yellow', 'attributes': {'ctermfg':'3','guifg':'#ffff00'}, 'normal':False},
    34: {'description':'Set foreground color to Blue', 'attributes': {'ctermfg':'4','guifg':'#0000ff'}, 'normal':False},
    35: {'description':'Set foreground color to Magenta', 'attributes': {'ctermfg':'5','guifg':'#990099'}, 'normal':False},
    36: {'description':'Set foreground color to Cyan', 'attributes': {'ctermfg':'6','guifg':'#009999'}, 'normal':False},
    37: {'description':'Set foreground color to White', 'attributes': {'ctermfg':'7','guifg':'#ffffff'}, 'normal':False},
    39: {'description':'Set foreground color to default (original)', 'attributes': {'ctermfg':'NONE','guifg':'NONE'}, 'normal':True},
    40: {'description':'Set background color to Black', 'attributes': {'ctermbg':'16','guibg':'#000000'}, 'normal':False},
    41: {'description':'Set background color to Red', 'attributes': {'ctermbg':'1','guibg':'#ff0000'}, 'normal':False},
    42: {'description':'Set background color to Green', 'attributes': {'ctermbg':'2','guibg':'#00ff00'}, 'normal':False},
    43: {'description':'Set background color to Yellow', 'attributes': {'ctermbg':'3','guibg':'#ffff00'}, 'normal':False},
    44: {'description':'Set background color to Blue', 'attributes': {'ctermbg':'4','guibg':'#0000ff'}, 'normal':False},
    45: {'description':'Set background color to Magenta', 'attributes': {'ctermbg':'5','guibg':'#990099'}, 'normal':False},
    46: {'description':'Set background color to Cyan', 'attributes': {'ctermbg':'6','guibg':'#009999'}, 'normal':False},
    47: {'description':'Set background color to White', 'attributes': {'ctermbg':'7','guibg':'#ffffff'}, 'normal':False},
    49: {'description':'Set background color to default (original).', 'attributes': {'ctermbg':'NONE','guibg':'NONE'}, 'normal':True},
    90: {'description':'Set foreground color to Black', 'attributes': {'ctermfg':'8','guifg':'#000000'}, 'normal':False},
    91: {'description':'Set foreground color to Red', 'attributes': {'ctermfg':'9','guifg':'#ff0000'}, 'normal':False},
    92: {'description':'Set foreground color to Green', 'attributes': {'ctermfg':'10','guifg':'#00ff00'}, 'normal':False},
    93: {'description':'Set foreground color to Yellow', 'attributes': {'ctermfg':'11','guifg':'#ffff00'}, 'normal':False},
    94: {'description':'Set foreground color to Blue', 'attributes': {'ctermfg':'12','guifg':'#0000ff'}, 'normal':False},
    95: {'description':'Set foreground color to Magenta', 'attributes': {'ctermfg':'13','guifg':'#990099'}, 'normal':False},
    96: {'description':'Set foreground color to Cyan', 'attributes': {'ctermfg':'14','guifg':'#009999'}, 'normal':False},
    97: {'description':'Set foreground color to White', 'attributes': {'ctermfg':'15','guifg':'#ffffff'}, 'normal':False},
    100: {'description':'Set background color to Black', 'attributes': {'ctermbg':'8','guibg':'#000000'}, 'normal':False},
    101: {'description':'Set background color to Red', 'attributes': {'ctermbg':'9','guibg':'#ff0000'}, 'normal':False},
    102: {'description':'Set background color to Green', 'attributes': {'ctermbg':'10','guibg':'#00ff00'}, 'normal':False},
    103: {'description':'Set background color to Yellow', 'attributes': {'ctermbg':'11','guibg':'#ffff00'}, 'normal':False},
    104: {'description':'Set background color to Blue', 'attributes': {'ctermbg':'12','guibg':'#0000ff'}, 'normal':False},
    105: {'description':'Set background color to Magenta', 'attributes': {'ctermbg':'13','guibg':'#990099'}, 'normal':False},
    106: {'description':'Set background color to Cyan', 'attributes': {'ctermbg':'14','guibg':'#009999'}, 'normal':False},
    107: {'description':'Set background color to White', 'attributes': {'ctermbg':'15','guibg':'#ffffff'}, 'normal':False}
} 
# }}}

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

    # screen object
    window          = None
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

    # enable colors
    enable_colors = True

    # color changes
    color_changes = {}

    # color history
    color_history = {}

    # don't wrap table output
    unwrap_tables = True

    # wrap CUF/CUB around line breaks
    wrap_cursor = True

    # }}}

    # constructor
    def __init__(self): # {{{
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

    # write to pty
    def write(self, input): # {{{
        logging.debug('writing input ' + str(input))

        # write and read
        self.proc.write(input)
        self.read(1)
        # }}}

    # read from pty, and update buffer
    def read(self, timeout = 1): # {{{
        # read from subprocess
        output = self.proc.read(timeout)
        # and strip null chars
        output = output.replace(chr(0), '')

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
            logging.debug('chgs ' + str(self.color_changes))
            logging.debug('at line ' + str(self.l) + ' column ' + str(self.c))
            logging.debug('current: ' + self.screen[self.l])

            # Check for control character match {{{
            if CONQUE_SEQ_REGEX_CTL.match(s[0]):
                logging.debug('control match')
                nr = ord(s[0])
                if nr in CONQUE_CTL:
                    getattr(self, 'ctl_' + CONQUE_CTL[nr])()
                else:
                    logging.debug('escape not found for ' + str(s))
                # }}}

            # check for escape sequence match {{{
            elif CONQUE_SEQ_REGEX_CSI.match(s):
                logging.debug('csi match')
                if s[-1] in CONQUE_ESCAPE:
                    csi = self.parse_csi(s[2:])
                    logging.debug(str(csi))
                    getattr(self, 'csi_' + CONQUE_ESCAPE[s[-1]])(csi)
                else:
                    logging.debug('escape not found for ' + str(s))
                # }}}
    
            # check for hash match {{{
            elif CONQUE_SEQ_REGEX_HASH.match(s):
                logging.debug('hash match')
                if s[-1] in CONQUE_ESCAPE_HASH:
                    csi = self.parse_csi(s[2:])
                    getattr(self, 'hash_' + CONQUE_ESCAPE_HASH[s[-1]])(csi)
                else:
                    logging.debug('escape not found for ' + str(s))
                # }}}
            
            # check for other escape match {{{
            elif CONQUE_SEQ_REGEX_ESC.match(s):
                logging.debug('escape match')
                if s[-1] in CONQUE_ESCAPE_PLAIN:
                    csi = self.parse_csi(s[1:])
                    getattr(self, 'esc_' + CONQUE_ESCAPE_PLAIN[s[-1]])(csi)
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

    # for polling
    def auto_read(self): # {{{
        self.read(1)
        vim.command('call feedkeys("\<F7>", "t")')
        self.screen.set_cursor(self.l, self.c)
    # }}}

    ###############################################################################################
    # Plain text # {{{

    def plain_text(self, input):
        logging.debug('plain -- ' + str(self.color_changes))
        current_line = self.screen[self.l]

        if len(current_line) < self.working_columns:
            current_line = current_line + ' ' * (self.c - len(current_line))

        # if line is wider than screen
        if self.c + len(input) - 1 > self.working_columns:
            # Table formatting hack
            if self.unwrap_tables and CONQUE_TABLE_OUTPUT.match(input):
                self.screen[self.l] = current_line[ : self.c - 1] + input + current_line[ self.c + len(input) - 1 : ]
                self.apply_color(self.c, self.c + len(input))
                self.c += len(input)
                return
            logging.debug('autowrap triggered')
            diff = self.c + len(input) - self.working_columns - 1
            # if autowrap is enabled
            if self.autowrap:
                self.screen[self.l] = current_line[ : self.c - 1] + input[ : -1 * diff ]
                self.apply_color(self.c, self.working_columns)
                self.ctl_nl()
                self.ctl_cr()
                self.plain_text(input[ -1 * diff : ])
            else:
                self.screen[self.l] = current_line[ : self.c - 1] + input[ : -1 * diff - 1 ] + input[-1]
                self.apply_color(self.c, self.working_columns)
                self.c = self.working_columns

        # no autowrap
        else:
            self.screen[self.l] = current_line[ : self.c - 1] + input + current_line[ self.c + len(input) - 1 : ]
            self.apply_color(self.c, self.c + len(input))
            self.c += len(input)

    def apply_color(self, start, end):
        logging.debug('applying colors ' + str(self.color_changes))

        # stop here if coloration is disabled
        if not self.enable_colors:
            return

        real_line = self.screen.get_real_line(self.l)
        unique_key = str(self.proc.pid)

        # clear colors if we're starting at col 1
        if start == 1 and self.color_history.has_key(real_line):
            for syn_name in self.color_history[real_line]:
                vim.command('syn clear ' + syn_name)

        # if there are no new colors
        if len(self.color_changes) == 0:
            return

        highlight = ''
        for attr in self.color_changes.keys():
            highlight = highlight + ' ' + attr + '=' + self.color_changes[attr]

        syntax_name = 'EscapeSequenceAt_' + unique_key + '_' + str(self.l) + '_' + str(start) + '_' + str(len(self.color_history) + 1)
        syntax_region = 'syntax match ' + syntax_name + ' /\%' + str(real_line) + 'l\%>' + str(start - 1) + 'c.*\%<' + str(end + 1) + 'c/ contains=ALL oneline'
        syntax_highlight = 'highlight ' + syntax_name + highlight

        vim.command(syntax_region)
        vim.command(syntax_highlight)

        # add syntax name to history
        if not self.color_history.has_key(real_line):
            self.color_history[real_line] = []

        self.color_history[real_line].append(syntax_name)

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

        self.color_changes = {}

    def ctl_cr(self):
        self.c = 1

        self.color_changes = {}

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
                ts = i + 1
                break

        logging.debug('tabbing from ' + str(self.c) + ' to ' + str(ts))

        self.c = ts

    # }}}

    ###############################################################################################
    # CSI functions {{{

    def csi_font(self, csi): # {{{
        if not self.enable_colors:
            return
        
        # defaults to 0
        if len(csi['vals']) == 0:
            csi['vals'] = [0]

        for val in csi['vals']:
            if CONQUE_FONT.has_key(val):
                logging.debug('color ' + str(CONQUE_FONT[val]))
                # ignore starting normal colors
                if CONQUE_FONT[val]['normal'] and len(self.color_changes) == 0:
                    logging.debug('a')
                    continue
                # clear color changes
                elif CONQUE_FONT[val]['normal']:
                    logging.debug('b')
                    self.color_changes = {}
                # save these color attributes for next plain_text() call
                else:
                    logging.debug('c')
                    for attr in CONQUE_FONT[val]['attributes'].keys():
                        if self.color_changes.has_key(attr) and (attr == 'cterm' or attr == 'gui'):
                            self.color_changes[attr] += ',' + CONQUE_FONT[val]['attributes'][attr]
                        else:
                            self.color_changes[attr] = CONQUE_FONT[val]['attributes'][attr]
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

        # clear colors
        if csi['val'] == 2 or (csi['val'] == 0 and self.c == 1):
            real_line = self.screen.get_real_line(self.l)
            if self.color_history.has_key(real_line):
                for syn_name in self.color_history[real_line]:
                    vim.command('syn clear ' + syn_name)

        logging.debug(str(self.color_changes))
        logging.debug('new line: ' + self.screen[self.l])
        # }}}

    def csi_cursor_right(self, csi): # {{{
        # we use 1 even if escape explicitly specifies 0
        if csi['val'] == 0:
            csi['val'] = 1

        logging.debug('working columns is ' + str(self.working_columns))
        logging.debug('new col is ' + str(self.c + csi['val']))

        if self.wrap_cursor and self.c + csi['val'] > self.working_columns:
            self.l += int(math.floor( (self.c + csi['val']) / self.working_columns ))
            self.c = (self.c + csi['val']) % self.working_columns
            return

        self.c = self.bound(self.c + csi['val'], 1, self.working_columns)
        # }}}

    def csi_cursor_left(self, csi): # {{{
        # we use 1 even if escape explicitly specifies 0
        if csi['val'] == 0:
            csi['val'] = 1

        if self.wrap_cursor and csi['val'] >= self.c:
            self.l += int(math.floor( (self.c - csi['val']) / self.working_columns ))
            self.c = self.working_columns - (csi['val'] - self.c) % self.working_columns
            return

        self.c = self.bound(self.c - csi['val'], 1, self.working_columns)
        # }}}

    def csi_cursor_to_column(self, csi): # {{{
        self.c = self.bound(csi['val'], 1, self.working_columns)
        # }}}

    def csi_cursor_up(self, csi): # {{{
        self.l = self.bound(self.l - csi['val'], self.top, self.bottom)

        self.color_changes = {}
        # }}}

    def csi_cursor_down(self, csi): # {{{
        self.l = self.bound(self.l + csi['val'], self.top, self.bottom)

        self.color_changes = {}
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

        # clear coloration
        if csi['val'] == 2 or csi['val'] == 0:
            real_line = self.screen.get_real_line(self.l)
            for line in self.color_history.keys():
                if line >= real_line:
                    for syn_name in self.color_history[line]:
                        vim.command('syn clear ' + syn_name)

        self.color_changes = {}
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

        # if cursor is outside scrolling region, reset it
        if self.l < self.top:
            self.l = self.top
        elif self.l > self.bottom:
            self.l = self.bottom

        self.color_changes = {}
        # }}}

    def csi_tab_clear(self, csi): # {{{
        # this escape defaults to 0
        if len(csi['vals']) == 0:
            csi['val'] = 0

        logging.debug('clearing tab with ' + str(csi['val']))

        if csi['val'] == 0:
            self.tabstops[self.c - 1] = False
        elif csi['val'] == 3:
            for i in range(0, self.columns + 1):
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


        self.color_changes = {}
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


        self.color_changes = {}
        # }}}

    # }}}

    ###############################################################################################
    # ESC functions {{{

    def esc_scroll_up(self, csi): # {{{
        self.ctl_nl()

        self.color_changes = {}
        # }}}

    def esc_next_line(self, csi): # {{{
        self.ctl_nl()
        self.c = 1
        # }}}

    def esc_set_tab(self, csi): # {{{
        logging.debug('set tab at ' + str(self.c))
        self.tabstops[self.c - 1] = True
        # }}}

    def esc_scroll_down(self, csi): # {{{
        if self.l == self.top:
            del self.screen[self.bottom]
            self.screen.insert(self.top, '')
        else:
            self.l += -1

        self.color_changes = {}
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
    # Random stuff {{{

    def paste(self):
        self.write(vim.eval('@@'))
        self.read(50)

    def paste_selection(self):
        self.write(vim.eval('@@'))

    def update_window_size(self):
        # resize if needed
        if self.window.width != self.columns or self.window.height != self.lines:

            # reset all window size attributes to default
            self.columns = self.window.width
            self.lines = self.window.height
            self.working_columns = self.window.width
            self.working_lines = self.window.height
            self.bottom = self.window.height

            # reset screen object attributes
            self.l = self.screen.reset_size(self.l)

            logging.debug('signal window resize here ---')

            # signal process that screen size has changed
            self.proc.window_resize(self.lines, self.columns)

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
                if val != '':
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

