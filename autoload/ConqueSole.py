
import vim, time, random

import logging # DEBUG
LOG_FILENAME = 'pylog.log' # DEBUG
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG) # DEBUG

# shared constants
CONQUE_SOLE_BUFFER_LENGTH = 1000
CONQUE_SOLE_INPUT_SIZE = 1000
CONQUE_SOLE_STATS_SIZE = 1000
CONQUE_SOLE_COMMANDS_SIZE = 255
CONQUE_SOLE_RESCROLL_SIZE = 255

# interval of screen redraw
# larger number means less frequent
CONQUE_SOLE_SCREEN_REDRAW = 10

# interval of full buffer redraw
# larger number means less frequent
CONQUE_SOLE_BUFFER_REDRAW = 500

###################################################################################################

class ConqueSole(Conque):

    window_top = None
    window_bottom = None

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
                self.plain_text(i, lines[i], attributes[i])

        # full screen redraw
        elif stats['cursor_y'] + 1 != self.l or stats['top_offset'] != self.window_top or random.randint(0, CONQUE_SOLE_SCREEN_REDRAW) == 0:
            update_top = self.window_top
            update_bottom = stats['top_offset'] + self.lines
            (lines, attributes) = self.proc.read(update_top, update_bottom - update_top)
            for i in range(update_top, update_bottom + 1):
                self.plain_text(i, lines[i], attributes[i])
            

        # single line redraw
        else:
            (lines, attributes) = self.proc.read(stats['cursor_y'], 1)
            if lines[0] != self.buffer[stats['cursor_y']]:
                self.plain_text(stats['cursor_y'], lines[0], attributes[0])

        # reset current position
        self.window_top = stats['top_offset']
        self.l = stats['cursor_y'] + 1
        self.c = stats['cursor_x'] + 1

        # reposition cursor if this seems plausible
        if set_cursor:
            self.set_cursor(self.l, self.c)

        # }}}

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

    def plain_text(self, line_nr, text, attributes):

        logging.debug('line ' + str(line_nr) + ": " + text)
        logging.debug('attributes ' + str(line_nr) + ": " + attributes)

        # remove trailing whitespace
        text = text.rstrip()

        # update vim buffer
        if len(self.buffer) <= line_nr:
            self.buffer.append(text)
        else:
            self.buffer[line_nr] = text

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


