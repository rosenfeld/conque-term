
import vim, time, random

import logging # DEBUG
LOG_FILENAME = 'pylog.log' # DEBUG
#logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG) # DEBUG

# Globals # {{{

# shared constants
CONQUE_SOLE_BUFFER_LENGTH = 1000
CONQUE_SOLE_INPUT_SIZE = 1000
CONQUE_SOLE_STATS_SIZE = 1000
CONQUE_SOLE_COMMANDS_SIZE = 255
CONQUE_SOLE_RESCROLL_SIZE = 255

# interval of screen redraw
# larger number means less frequent
CONQUE_SOLE_SCREEN_REDRAW = 100

# interval of full buffer redraw
# larger number means less frequent
CONQUE_SOLE_BUFFER_REDRAW = 500

# }}}

###################################################################################################

class ConqueSole(Conque):

    window_top = None
    window_bottom = None

    color_cache = {}

    buffer = None

    # *********************************************************************************************
    # start program and initialize this instance

    def open(self, command, options = {}): # {{{

        # init size
        self.columns = vim.current.window.width
        self.lines = vim.current.window.height
        self.window_top = 0
        self.window_bottom = vim.current.window.height - 1

        # init color
        self.enable_colors = options['color']

        # open command
        self.proc = ConqueSoleWrapper()
        self.proc.open(command, { 'TERM' : options['TERM'], 'CONQUE' : '1', 'LINES' : self.lines, 'COLUMNS' : self.columns })

        self.buffer = vim.current.buffer

        # }}}


    # *********************************************************************************************
    # read and update screen

    def read(self, timeout = 1, set_cursor = True): # {{{

        stats = self.proc.get_stats()

        if not stats:
            return

        # full buffer redraw, our favorite!
        if random.randint(0, CONQUE_SOLE_BUFFER_REDRAW) == 0:
            update_bottom = stats['top_offset'] + self.lines
            (lines, attributes) = self.proc.read(0, update_bottom)
            for i in range(0, update_bottom + 1):
                self.plain_text(i, lines[i], attributes[i], stats)

        # full screen redraw
        elif stats['cursor_y'] + 1 != self.l or stats['top_offset'] != self.window_top or random.randint(0, CONQUE_SOLE_SCREEN_REDRAW) == 0:
            update_top = self.window_top
            update_bottom = stats['top_offset'] + self.lines
            (lines, attributes) = self.proc.read(update_top, update_bottom - update_top)
            for i in range(update_top, update_bottom + 1):
                self.plain_text(i, lines[i - update_top], attributes[i - update_top], stats)
            

        # single line redraw
        else:
            (lines, attributes) = self.proc.read(stats['cursor_y'], 1)
            if lines[0] != self.buffer[stats['cursor_y']]:
                self.plain_text(stats['cursor_y'], lines[0], attributes[0], stats)

        # reset current position
        self.window_top = stats['top_offset']
        self.l = stats['cursor_y'] + 1
        self.c = stats['cursor_x'] + 1

        # reposition cursor if this seems plausible
        if set_cursor:
            self.set_cursor(self.l, self.c)

        # }}}

    #########################################################################
    # for polling

    def auto_read(self): # {{{

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

    #########################################################################
    # update the buffer

    def plain_text(self, line_nr, text, attributes, stats): # {{{

        #logging.debug('line ' + str(line_nr) + ": " + text)
        #logging.debug('attributes ' + str(line_nr) + ": " + attributes)
        #logging.debug('default attr ' + str(stats['default_attribute']))

        self.l = line_nr + 1

        # remove trailing whitespace
        text = text.rstrip()

        # update vim buffer
        if len(self.buffer) <= line_nr:
            self.buffer.append(text)
        else:
            self.buffer[line_nr] = text

        self.do_color(attributes = attributes, stats = stats)

        # }}}

    #########################################################################

    def do_color(self, start = 0, end = 0, attributes = '', stats = None): # {{{

        # stop here if coloration is disabled
        if not self.enable_colors:
            return

        # if no colors for this line, clear everything out
        if len(attributes) == 0 or attributes == unichr(stats['default_attribute']) * len(attributes):
            self.color_changes = {}
            self.apply_color(1, len(attributes), self.l)
            return

        # if text attribute is different, call add_color()
        attr = None
        start = 0
        for i in range(0, len(attributes)):
            c = ord(attributes[i])
            #logging.debug('attr char ' + str(c))
            if c != attr:
                if attr and attr != stats['default_attribute']:
                    self.color_changes = self.translate_color(attr)
                    self.apply_color(start + 1, i + 1, self.l)
                start = i
                attr = c

        if attr and attr != stats['default_attribute']:
            self.color_changes = self.translate_color(attr)
            self.apply_color(start + 1, len(attributes), self.l)


        # }}}

    #########################################################################

    def translate_color(self, attr): # {{{

        # check for cached color
        if attr in self.color_cache:
            return self.color_cache[attr]

        #logging.debug('adding color at line ' + str(line_nr))
        #logging.debug('start ' + str(start))
        #logging.debug('start ' + str(end))
        #logging.debug('attr ' + str(attr))

        # convert attribute integer to bit string
        bit_str = bin(attr)
        bit_str = bit_str.replace('0b', '')

        # slice foreground and background portions of bit string
        fg = bit_str[-4:].rjust(4, '0')
        bg = bit_str[-8:-4].rjust(4, '0')

        # ok, first create foreground #rbg
        red    = int(fg[1]) * 204 + int(fg[0]) * 51
        green  = int(fg[2]) * 204 + int(fg[0]) * 51
        blue   = int(fg[3]) * 204 + int(fg[0]) * 51
        fg_str = "#%02x%02x%02x" % (red, green, blue)

        # ok, first create foreground #rbg
        red    = int(bg[1]) * 204 + int(bg[0]) * 51
        green  = int(bg[2]) * 204 + int(bg[0]) * 51
        blue   = int(bg[3]) * 204 + int(bg[0]) * 51
        bg_str = "#%02x%02x%02x" % (red, green, blue)

        # build value for color_changes
    
        color = { 'guifg' : fg_str, 'guibg' : bg_str }

        self.color_cache[attr] = color

        return color

        # }}}

    #########################################################################
    # write virtual key code to shared memory using proprietary escape seq

    def write_vk(self, vk_code): # {{{

        self.proc.write_vk(vk_code)

          

        # }}}

    # *********************************************************************************************
    # resize if needed

    def update_window_size(self): # {{{
        pass

        # }}}

    # *********************************************************************************************
    # resize if needed

    def set_cursor(self, line, column): # {{{

        # figure out line
        real_line = line
        if real_line > len(self.buffer):
            for l in range(len(self.buffer) - 1, real_line):
                self.buffer.append('')

        # figure out column 
        real_column = column
        if len(self.buffer[real_line - 1]) < real_column:
            self.buffer[real_line - 1] = self.buffer[real_line - 1] + ' ' * (real_column - len(self.buffer[real_line - 1]))

        # python version is occasionally grumpy
        try:
            vim.current.window.cursor = (real_line, real_column - 1)
        except:
            vim.command('call cursor(' + str(real_line) + ', ' + str(real_column) + ')')
    # }}}


    # *********************************************************************************************
    # go into idle mode

    def idle(self): # {{{

        self.proc.idle()

        # }}}

    # *********************************************************************************************
    # resume from idle mode

    def resume(self): # {{{

        self.proc.resume()

        # }}}


