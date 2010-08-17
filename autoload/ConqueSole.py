
import vim, time, random
from ConqueSoleSubprocess import * # DEBUG

import logging # DEBUG
LOG_FILENAME = 'pylog.log' # DEBUG
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG) # DEBUG

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

        # multi-line changes: go mad!
        if stats['cursor_y'] != self.l or stats['top_offset'] != self.window_top or random.randint(0,9) == 0:
            update_top = self.window_top
            update_bottom = stats['top_offset'] + self.lines
            lines = self.proc.read(update_top, update_bottom - update_top)
            for i in range(update_top, update_bottom + 1):
                #logging.debug('setting line ' + str(i) + ' to: ' + lines[i - update_top])
                if i == len(self.buffer):
                    self.buffer.append(lines[i - update_top].rstrip())
                else:
                    self.buffer[i] = lines[i - update_top].rstrip()
            

        # otherwise just update this line
        else:
            lines = self.proc.read(self.l, 1)
            if lines[0] != self.buffer[self.l]:
                self.buffer[self.l] = lines[0].rstrip()

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


