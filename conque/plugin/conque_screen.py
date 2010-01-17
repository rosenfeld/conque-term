# ConqueScreen is an extention of the vim.current.buffer object
# It restricts the working indices of the buffer object to the scroll region which pty is expecting
# It also uses 1-based indexes, to match escape sequence commands
#
# E.g.:
#   s = ConqueScreen()
#   ...
#   s[5] = 'Set 5th line in terminal to this line'
#   s.append('Add new line to terminal')
#   s[5] = 'Since previous append() command scrolled the terminal down, this is a different line than first cb[5] call'
#

###################################################################################################
class ConqueScreen(object):

    # CLASS PROPERTIES  {{{

    # the buffer
    buffer          = None
    window          = None

    # screen and scrolling regions
    screen_top      = 1

    # screen width
    screen_width    = 80
    screen_height    = 80

    # }}}

    def __init__(self): # {{{
        self.buffer = vim.current.buffer
        self.window = vim.current.window

        self.screen_top = 1
        self.screen_width = self.window.width
        self.screen_height = self.window.height

    # }}}

    # LIST OVERLOAD {{{
    def __len__(self):
        return len(self.buffer)

    def __getitem__(self, key):
        real_line = self.screen_top + key - 2
        #logging.debug('getitem ' + str(key) + ' translates to ' + str(self.screen_top) + ' + ' + str(key) + ' - ' + str(2) + ' = ' + str(real_line))
        if real_line >= len(self.buffer):
            #logging.debug('need to append')
            for i in range(len(self.buffer), real_line + 1):
                #logging.debug('appending')
                self.append(' ' * self.screen_width)
        return self.buffer[ real_line ]

    def __setitem__(self, key, value):
        real_line = self.screen_top + key - 2
        #logging.debug('set key is ' + str(key))
        #logging.debug('used val is ' + str(real_line))
        if real_line == len(self.buffer):
            self.buffer.append(value)
        else:
            self.buffer[ real_line ] = value

    def __delitem__(self, key):
        del self.buffer[ self.screen_top + key - 2 ]

    def append(self, value):
        self.buffer.append(value)
        logging.debug('checking new line ' + str(len(self.buffer)) + ' against top ' + str(self.screen_top) + ' + height ' + str(self.screen_height) + ' - 1 = ' + str(self.screen_top + self.screen_height - 1))
        if len(self.buffer) > self.screen_top + self.screen_height - 1:
            self.screen_top += 1
            vim.command('normal G')

    def insert(self, line, value):
        logging.debug('insert at line ' + str(self.screen_top + line - 2))
        l = self.screen_top + line - 2
        self.buffer[l:l] = [ value ]
    
    # }}}

    def set_screen_width(self, width):
        self.screen_width = width

    def clear(self):
        self.buffer.append(' ')
        vim.command('normal Gzt')
        self.screen_top = len(self.buffer)

    def get_top(self):
        return self.screen_top

    def get_real_line(self, line):
        return (self.screen_top + line - 1)

    def set_cursor(self, line, column):
        # figure out line
        real_line =  self.screen_top + line - 1
        if real_line > len(self.buffer):
            for l in range(len(self.buffer) - 1, real_line):
                self.buffer.append('')

        # figure out column
        real_column = column
        if len(self.buffer[real_line - 1]) < real_column:
            self.buffer[real_line - 1] = self.buffer[real_line - 1] + ' ' * (real_column - len(self.buffer[real_line - 1]))

        # XXX - Using python's version makes lots of super-fun segfaults
        self.window.cursor = (real_line, real_column - 1)
        #vim.command('call cursor(' + str(real_line) + ', ' + str(real_column) + ')')

    def reset_size(self, line):
        logging.debug('buffer len is ' + str(len(self.buffer)))
        logging.debug('buffer height ' + str(self.window.height))
        logging.debug('old screen top was ' + str(self.screen_top))

        # save cursor line number
        real_line = self.screen_top + line

        # reset screen size
        self.screen_width = self.window.width
        self.screen_height = self.window.height
        self.screen_top = len(self.buffer) - self.window.height + 1
        if self.screen_top < 1:
            self.screen_top = 1
        logging.debug('new screen top is  ' + str(self.screen_top))

        # align bottom of buffer to bottom of screen
        vim.command('normal ' + str(self.screen_height) + 'kG')

        # return new relative line number
        return (real_line - self.screen_top)

    def scroll_to_bottom(self):
        self.window.cursor = (len(self.buffer) - 1, 1)
        

