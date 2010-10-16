
import vim, re, time, math

import logging # DEBUG
LOG_FILENAME = '/Users/nraffo/.vim/pylog.log' # DEBUG
#logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG) # DEBUG

# CONFIG CONSTANTS  {{{

CONQUE_CTL = {
     1:'soh', # start of heading
     2:'stx', # start of text
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

# Character set escape sequences, with "("
CONQUE_ESCAPE_CHARSET = {
    'A':'uk',
    'B':'us',
    '0':'graphics'
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
    '8':'screen_alignment_test'
} 
#    '3':'double_height_top',
#    '4':'double_height_bottom',
#    '5':'single_height_single_width',
#    '6':'single_height_double_width',

CONQUE_GRAPHICS_SET = [
    0x0000, 0x0001, 0x0002, 0x0003, 0x0004, 0x0005, 0x0006, 0x0007,
    0x0008, 0x0009, 0x000A, 0x000B, 0x000C, 0x000D, 0x000E, 0x000F,
    0x0010, 0x0011, 0x0012, 0x0013, 0x0014, 0x0015, 0x0016, 0x0017,
    0x0018, 0x0019, 0x001A, 0x001B, 0x001C, 0x001D, 0x001E, 0x001F,
    0x0020, 0x0021, 0x0022, 0x0023, 0x0024, 0x0025, 0x0026, 0x0027,
    0x0028, 0x0029, 0x002A, 0x2192, 0x2190, 0x2191, 0x2193, 0x002F,
    0x2588, 0x0031, 0x0032, 0x0033, 0x0034, 0x0035, 0x0036, 0x0037,
    0x0038, 0x0039, 0x003A, 0x003B, 0x003C, 0x003D, 0x003E, 0x003F,
    0x0040, 0x0041, 0x0042, 0x0043, 0x0044, 0x0045, 0x0046, 0x0047,
    0x0048, 0x0049, 0x004A, 0x004B, 0x004C, 0x004D, 0x004E, 0x004F,
    0x0050, 0x0051, 0x0052, 0x0053, 0x0054, 0x0055, 0x0056, 0x0057,
    0x0058, 0x0059, 0x005A, 0x005B, 0x005C, 0x005D, 0x005E, 0x00A0,
    0x25C6, 0x2592, 0x2409, 0x240C, 0x240D, 0x240A, 0x00B0, 0x00B1,
    0x2591, 0x240B, 0x2518, 0x2510, 0x250C, 0x2514, 0x253C, 0xF800,
    0xF801, 0x2500, 0xF803, 0xF804, 0x251C, 0x2524, 0x2534, 0x252C,
    0x2502, 0x2264, 0x2265, 0x03C0, 0x2260, 0x00A3, 0x00B7, 0x007F,
    0x0080, 0x0081, 0x0082, 0x0083, 0x0084, 0x0085, 0x0086, 0x0087,
    0x0088, 0x0089, 0x008A, 0x008B, 0x008C, 0x008D, 0x008E, 0x008F,
    0x0090, 0x0091, 0x0092, 0x0093, 0x0094, 0x0095, 0x0096, 0x0097,
    0x0098, 0x0099, 0x009A, 0x009B, 0x009C, 0x009D, 0x009E, 0x009F,
    0x00A0, 0x00A1, 0x00A2, 0x00A3, 0x00A4, 0x00A5, 0x00A6, 0x00A7,
    0x00A8, 0x00A9, 0x00AA, 0x00AB, 0x00AC, 0x00AD, 0x00AE, 0x00AF,
    0x00B0, 0x00B1, 0x00B2, 0x00B3, 0x00B4, 0x00B5, 0x00B6, 0x00B7,
    0x00B8, 0x00B9, 0x00BA, 0x00BB, 0x00BC, 0x00BD, 0x00BE, 0x00BF,
    0x00C0, 0x00C1, 0x00C2, 0x00C3, 0x00C4, 0x00C5, 0x00C6, 0x00C7,
    0x00C8, 0x00C9, 0x00CA, 0x00CB, 0x00CC, 0x00CD, 0x00CE, 0x00CF,
    0x00D0, 0x00D1, 0x00D2, 0x00D3, 0x00D4, 0x00D5, 0x00D6, 0x00D7,
    0x00D8, 0x00D9, 0x00DA, 0x00DB, 0x00DC, 0x00DD, 0x00DE, 0x00DF,
    0x00E0, 0x00E1, 0x00E2, 0x00E3, 0x00E4, 0x00E5, 0x00E6, 0x00E7,
    0x00E8, 0x00E9, 0x00EA, 0x00EB, 0x00EC, 0x00ED, 0x00EE, 0x00EF,
    0x00F0, 0x00F1, 0x00F2, 0x00F3, 0x00F4, 0x00F5, 0x00F6, 0x00F7,
    0x00F8, 0x00F9, 0x00FA, 0x00FB, 0x00FC, 0x00FD, 0x00FE, 0x00FF
]

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
CONQUE_SEQ_REGEX       = re.compile(u("(\x1b\[?\??#?[0-9;]*[a-zA-Z0-9@=>]|\x1b\][0-9];.*?\x07|[\x01-\x0f])"), re.UNICODE)
CONQUE_SEQ_REGEX_CTL   = re.compile(u("^[\x01-\x0f]$"), re.UNICODE)
CONQUE_SEQ_REGEX_CSI   = re.compile(u("^\x1b\["), re.UNICODE)
CONQUE_SEQ_REGEX_TITLE = re.compile(u("^\x1b\]"), re.UNICODE)
CONQUE_SEQ_REGEX_HASH  = re.compile(u("^\x1b#"), re.UNICODE)
CONQUE_SEQ_REGEX_ESC   = re.compile(u("^\x1b.$"), re.UNICODE)
CONQUE_SEQ_REGEX_CHAR  = re.compile(u("^\x1b\("), re.UNICODE)

# match table output
CONQUE_TABLE_OUTPUT   = re.compile("^\s*\|\s.*\s\|\s*$|^\s*\+[=+-]+\+\s*$")

# }}}

###################################################################################################
class Conque:

    # CLASS PROPERTIES {{{ 

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

    # enable colors
    enable_colors = True

    # color changes
    color_changes = {}

    # color history
    color_history = {}

    # don't wrap table output
    unwrap_tables = True

    # wrap CUF/CUB around line breaks
    wrap_cursor = False

    # do we need to move the cursor?
    cursor_set = False

    # current character set, ascii or graphics
    character_set = 'ascii'

    # used for auto_read actions
    read_count = 0

    # }}}

    # constructor
    def __init__(self): # {{{
        self.screen = ConqueScreen()
        # }}}

    # start program and initialize this instance
    def open(self, command, options): # {{{

        # int vars
        self.columns = vim.current.window.width
        self.lines = vim.current.window.height
        self.working_columns = vim.current.window.width
        self.working_lines = vim.current.window.height
        self.bottom = vim.current.window.height

        # init color
        self.enable_colors = options['color']

        # init tabstops
        self.init_tabstops()

        # open command
        self.proc = ConqueSubprocess()
        self.proc.open(command, { 'TERM' : options['TERM'], 'CONQUE' : '1', 'LINES' : str(self.lines), 'COLUMNS' : str(self.columns)})

        # send window size signal, in case LINES/COLUMNS is ignored
        self.update_window_size(True)
        # }}}

    # write to pty
    def write(self, input, set_cursor = True, read = True): # {{{

        # check if window size has changed
        if read:
            self.update_window_size()

        # write and read
        self.proc.write(input)

        # read output immediately
        if read:
            self.read(1, set_cursor)

        # }}}

    # read from pty, and update buffer
    def read(self, timeout = 1, set_cursor = True, return_output = False, update_buffer = True): # {{{
        # read from subprocess
        output = self.proc.read(timeout)
        # and strip null chars
        output = output.replace(chr(0), '')

        if output == '':
            return

        # for bufferless terminals
        if not update_buffer:
            return output

        logging.debug('read *********************************************************************')
        #logging.debug(str(output))
        debug_profile_start = time.time()

        chunks = CONQUE_SEQ_REGEX.split(output)
        logging.debug('ouput chunking took ' + str((time.time() - debug_profile_start) * 1000) + ' ms')
        logging.debug(str(chunks))

        debug_profile_start = time.time()

        # don't go through all the csi regex if length is one (no matches)
        if len(chunks) == 1:
            logging.debug('short circuit')
            self.plain_text(chunks[0])

        else:
            for s in chunks:
                if s == '':
                    continue

                #logging.debug(str(s) + '--------------------------------------------------------------')
                logging.debug('chgs ' + str(self.color_changes))
                logging.debug('at line ' + str(self.l) + ' column ' + str(self.c))

                # Check for control character match {{{
                if CONQUE_SEQ_REGEX_CTL.match(s[0]):
                    logging.debug('control match')
                    nr = ord(s[0])
                    if nr in CONQUE_CTL:
                        getattr(self, 'ctl_' + CONQUE_CTL[nr])()
                    else:
                        logging.debug('escape not found for ' + str(s))
                        pass
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
                        pass
                    # }}}
        
                # check for title match {{{
                elif CONQUE_SEQ_REGEX_TITLE.match(s):
                    logging.debug('title match')
                    self.change_title(s[2], s[4:-1])
                    # }}}
        
                # check for hash match {{{
                elif CONQUE_SEQ_REGEX_HASH.match(s):
                    logging.debug('hash match')
                    if s[-1] in CONQUE_ESCAPE_HASH:
                        getattr(self, 'hash_' + CONQUE_ESCAPE_HASH[s[-1]])()
                    else:
                        logging.debug('escape not found for ' + str(s))
                        pass
                    # }}}
                
                # check for charset match {{{
                elif CONQUE_SEQ_REGEX_CHAR.match(s):
                    logging.debug('char match')
                    if s[-1] in CONQUE_ESCAPE_CHARSET:
                        getattr(self, 'charset_' + CONQUE_ESCAPE_CHARSET[s[-1]])()
                    else:
                        logging.debug('escape not found for ' + str(s))
                        pass
                    # }}}
                
                # check for other escape match {{{
                elif CONQUE_SEQ_REGEX_ESC.match(s):
                    logging.debug('escape match')
                    if s[-1] in CONQUE_ESCAPE_PLAIN:
                        getattr(self, 'esc_' + CONQUE_ESCAPE_PLAIN[s[-1]])()
                    else:
                        logging.debug('escape not found for ' + str(s))
                        pass
                    # }}}
                
                # else process plain text {{{
                else:
                    self.plain_text(s)
                    # }}}

        # check window size
        if set_cursor:
          self.screen.set_cursor(self.l, self.c)
        
        # we need to set the cursor position
        self.cursor_set = False

        vim.command('redraw')

        logging.info('::: read took ' + str((time.time() - debug_profile_start) * 1000) + ' ms')

        if return_output:
            return output
    # }}}

    # for polling
    def auto_read(self): # {{{

        # check subprocess status, but not every time since it's CPU expensive
        if self.read_count == 10:
            if not self.proc.is_alive():
                vim.command('call conque_term#get_instance().close()')
                return
            else:
                self.read_count = 0
        self.read_count += 1

        # read output
        self.read(1)

        # reset timer
        if self.c == 1:
            vim.command('call feedkeys("\<right>\<left>", "n")')
        else:
            vim.command('call feedkeys("\<left>\<right>", "n")')

        # stop here if cursor doesn't need to be moved
        if self.cursor_set:
            return
        
        # otherwise set cursor position
        self.set_cursor(self.l, self.c)
        self.cursor_set = True
    # }}}

    ###############################################################################################
    # Plain text # {{{

    def plain_text(self, input):

        # translate input into correct character set
        if self.character_set == 'graphics':
            old_input = input
            input = ''
            for i in range(0, len(old_input)):
                input = input + unichr(CONQUE_GRAPHICS_SET[ord(old_input[i])])

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
                remaining = input[ -1 * diff : ]
                logging.debug('remaining text: "' + remaining + '"')
                self.plain_text(remaining)
            else:
                self.screen[self.l] = current_line[ : self.c - 1] + input[ : -1 * diff - 1 ] + input[-1]
                self.apply_color(self.c, self.working_columns)
                self.c = self.working_columns

        # no autowrap
        else:
            self.screen[self.l] = current_line[ : self.c - 1] + input + current_line[ self.c + len(input) - 1 : ]
            self.apply_color(self.c, self.c + len(input))
            self.c += len(input)

    def apply_color(self, start, end, line = 0):
        logging.debug('applying colors ' + str(self.color_changes))

        # stop here if coloration is disabled
        if not self.enable_colors:
            return

        # allow custom line nr to be passed
        if line:
            real_line = line
        else:
            real_line = self.screen.get_real_line(self.l)

        # check for previous overlapping coloration
        logging.debug('start ' + str(start) + ' end ' + str(end))
        to_del = []
        if real_line in self.color_history:
            for i in range(len(self.color_history[real_line])):
                syn = self.color_history[real_line][i]
                logging.debug('checking syn ' + str(syn))
                if syn['start'] >= start and syn['start'] < end:
                    logging.debug('first')
                    vim.command('syn clear ' + syn['name'])
                    to_del.append(i)
                    # outside
                    if syn['end'] > end:
                        logging.debug('first.half')
                        self.exec_highlight(real_line, end, syn['end'], syn['highlight'])
                elif syn['end'] > start and syn['end'] <= end:
                    logging.debug('second')
                    vim.command('syn clear ' + syn['name'])
                    to_del.append(i)
                    # outside
                    if syn['start'] < start:
                        logging.debug('second.half')
                        self.exec_highlight(real_line, syn['start'], start, syn['highlight'])

        if len(to_del) > 0:
            to_del.reverse()
            for di in to_del:
                del self.color_history[real_line][di]

        # if there are no new colors
        if len(self.color_changes) == 0:
            return

        highlight = ''
        for attr in self.color_changes.keys():
            highlight = highlight + ' ' + attr + '=' + self.color_changes[attr]

        # execute the highlight
        self.exec_highlight(real_line, start, end, highlight)

    def exec_highlight(self, real_line, start, end, highlight):
        unique_key = str(self.proc.pid)

        syntax_name = 'EscapeSequenceAt_' + unique_key + '_' + str(self.l) + '_' + str(start) + '_' + str(len(self.color_history) + 1)
        syntax_options = ' contains=ALLBUT,ConqueString,MySQLString,MySQLKeyword oneline'
        syntax_region = 'syntax match ' + syntax_name + ' /\%' + str(real_line) + 'l\%>' + str(start - 1) + 'c.*\%<' + str(end + 1) + 'c/' + syntax_options
        syntax_highlight = 'highlight ' + syntax_name + highlight

        vim.command(syntax_region)
        vim.command(syntax_highlight)

        # add syntax name to history
        if not real_line in self.color_history:
            self.color_history[real_line] = []

        self.color_history[real_line].append({'name':syntax_name, 'start':start, 'end':end, 'highlight':highlight})

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

    def ctl_soh(self):
        pass

    def ctl_stx(self):
        pass

    def ctl_bel(self):
        vim.command('call conque_term#bell()')

    def ctl_tab(self):
        # default tabstop location
        ts = self.working_columns

        # check set tabstops
        for i in range(self.c, len(self.tabstops)):
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

        # 256 xterm color foreground
        if len(csi['vals']) == 3 and csi['vals'][0] == 38 and csi['vals'][1] == 5:
            self.color_changes['ctermfg'] = str(csi['vals'][2])
            self.color_changes['guifg'] = '#' + self.xterm_to_rgb(csi['vals'][2])

        # 256 xterm color background
        elif len(csi['vals']) == 3 and csi['vals'][0] == 48 and csi['vals'][1] == 5:
            self.color_changes['ctermbg'] = str(csi['vals'][2])
            self.color_changes['guibg'] = '#' + self.xterm_to_rgb(csi['vals'][2])

        # 16 colors
        else:
            for val in csi['vals']:
                if val in CONQUE_FONT:
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
                            if attr in self.color_changes and (attr == 'cterm' or attr == 'gui'):
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
            if real_line in self.color_history:
                for syn in self.color_history[real_line]:
                    vim.command('syn clear ' + syn['name'])

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
                    for syn in self.color_history[line]:
                        vim.command('syn clear ' + syn['name'])

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
            new_end = vim.current.window.height

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

    def esc_scroll_up(self): # {{{
        self.ctl_nl()

        self.color_changes = {}
        # }}}

    def esc_next_line(self): # {{{
        self.ctl_nl()
        self.c = 1
        # }}}

    def esc_set_tab(self): # {{{
        logging.debug('set tab at ' + str(self.c))
        if self.c <= len(self.tabstops):
            self.tabstops[self.c - 1] = True
        # }}}

    def esc_scroll_down(self): # {{{
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

    def hash_screen_alignment_test(self): # {{{
        self.csi_clear_screen(self.parse_csi('2J'))
        self.working_lines = self.lines
        for l in range(1, self.lines + 1):
            self.screen[l] = 'E' * self.working_columns
        # }}}

    # }}}

    ###############################################################################################
    # CHARSET functions {{{

    def charset_us(self):
        self.character_set = 'ascii'

    def charset_uk(self):
        self.character_set = 'ascii'

    def charset_graphics(self):
        self.character_set = 'graphics'

    # }}}

    ###############################################################################################
    # Random stuff {{{

    def set_cursor(self, line, col):
        self.screen.set_cursor(line, col)

    def change_title(self, key, val):
        logging.debug(key)
        logging.debug(val)
        if key == '0' or key == '2':
            logging.debug('setting title to ' + re.escape(val))
            vim.command('setlocal statusline=' + re.escape(val))
            try:
                vim.command('set titlestring=' + re.escape(val))
            except:
                pass

    def paste(self):
        self.write(vim.eval('@@'))
        self.read(50)

    def paste_selection(self):
        self.write(vim.eval('@@'))

    def update_window_size(self, force = False):
        # resize if needed
        if force or vim.current.window.width != self.columns or vim.current.window.height != self.lines:

            # reset all window size attributes to default
            self.columns = vim.current.window.width
            self.lines = vim.current.window.height
            self.working_columns = vim.current.window.width
            self.working_lines = vim.current.window.height
            self.bottom = vim.current.window.height

            # reset screen object attributes
            self.l = self.screen.reset_size(self.l)

            # reset tabstops
            self.init_tabstops()

            logging.debug('signal window resize here ---')

            # signal process that screen size has changed
            self.proc.window_resize(self.lines, self.columns)

    def insert_enter(self):

        # check window size
        self.update_window_size()
        
        # we need to set the cursor position
        self.cursor_set = False


    def init_tabstops(self):
        for i in range(0, self.columns + 1):
            if i % 8 == 0:
                self.tabstops.append(True)
            else:
                self.tabstops.append(False)

    def idle(self):
        pass

    def resume(self):
        pass

    def close (self):
        self.proc.close()

    def abort(self):
        self.proc.signal(1)

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
                logging.debug(val)
                val = re.sub("\D", "", val)
                logging.debug(val)
                if val != '':
                    attr['vals'].append(int(val))

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

    def xterm_to_rgb(self, color_code): # {{{
        if color_code < 16:
            ascii_colors = ['000000', 'CD0000', '00CD00', 'CDCD00', '0000EE', 'CD00CD', '00CDCD', 'E5E5E5', 
                   '7F7F7F', 'FF0000', '00FF00', 'FFFF00', '5C5CFF', 'FF00FF', '00FFFF', 'FFFFFF']
            return ascii_colors[color_code]

        elif color_code < 232:
            cc = int(color_code) - 16

            p1 = "%02x" % (math.floor(cc / 36) * (255/5))
            p2 = "%02x" % (math.floor((cc % 36) / 6) * (255/5))
            p3 = "%02x" % (math.floor(cc % 6) * (255/5))

            return p1 + p2 + p3
        else:
            grey_tone = "%02x" % math.floor((255/24) * (color_code - 232))
            return grey_tone + grey_tone + grey_tone
        # }}}

    # }}}

