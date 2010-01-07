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
    screen_bottom   = 1
    scroll_top      = 1
    scroll_bottom   = 1

    # screen width
    screen_width    = 80

    # }}}

    def __init__(self): # {{{
        self.buffer = vim.current.buffer
        self.window = vim.current.window

        self.screen_bottom = self.window.height
        self.scroll_bottom = self.window.height

        self.screen_width = self.window.width

    # }}}

    # LIST OVERLOAD {{{
    def __len__(self):
        return self.scroll_bottom - self.scroll_top + 1

    def __getitem__(self, key):
        real_line = self.scroll_top + key - 2
        logging.debug('getitem ' + str(key) + ' translates to ' + str(self.scroll_top) + ' + ' + str(key) + ' - ' + str(2) + ' = ' + str(real_line))
        if real_line >= len(self.buffer):
            logging.debug('need to append')
            for i in range(len(self.buffer), real_line + 1):
                logging.debug('appending')
                self.buffer.append('')
        return self.buffer[ real_line ]

    def __setitem__(self, key, value):
        self.buffer[ self.scroll_top + key - 2 ] = value

    def __delitem__(self, key):
        self.buffer.scroll_bottom.append('')
        del self.buffer[ self.scroll_top + key - 2 ]

    def append(self, value):
        print "not implemented"

    def insert(self, line, value):
        self.buffer.insert(self.scroll_top + line - 2, value)
    
    # }}}

    def set_scroll_region(self, top, bottom):
        self.scroll_top = self.screen_top + top - 1
        self.scroll_bottom = self.screen_bottom + bottom - 1

    def set_screen_width(self, width):
        self.screen_width = width

