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

    # autowrap mode
    auto_wrap       = 1

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
        if isinstance(key, slice):
            return self.buffer[ self.scroll_top + key.start - 1 : self.scroll_top + key.stop - 1 ]
        else:
            return self.buffer[ self.scroll_top + key - 1 ]

    def __setitem__(self, key, value):
        if isinstance(key, slice):
            self.buffer[ self.scroll_top + key.start - 1 : self.scroll_top + key.stop - 1 ] = value
        else:
            self.buffer[ self.scroll_top + key - 1 ] = value

    def __delitem__(self, key):
        if isinstance(key, slice):
            for i in range(key.start, key.stop):
                self.buffer.scroll_bottom.append('')
            del self.buffer[ self.scroll_top + key.start - 1 : self.scroll_top + key.stop - 1 ]
        else:
            self.buffer.scroll_bottom.append('')
            del self.buffer[ self.scroll_top + key - 1 ]

    def append(self, value):
        if self.scroll_top > self.screen_top or self.scroll_bottom < self.screen_bottom:
            self.buffer.scroll_bottom.append(value)
            if isinstance(value, list):
                for i in range(key.start, key.stop):
                    del self.buffer[ self.scroll_top ]
            else:
                del self.buffer[ self.scroll_top ]
        else:
            self.buffer.append(value)
    
    # }}}

    def set_scroll_region(self, top, bottom):
        self.scroll_top = self.screen_top + top - 1
        self.scroll_bottom = self.screen_bottom + bottom - 1

    def set_screen_width(self, width):
        self.screen_width = width

    def set_auto_wrap(self, auto_wrap):
        self.auto_wrap = auto_wrap



