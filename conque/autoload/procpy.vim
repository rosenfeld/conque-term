" FILE:     autoload/proc_py.vim
" AUTHOR:   Nico Raffo <nicoraffo@gmail.com>
" MODIFIED: __MODIFIED__
" VERSION:  __VERSION__, for Vim 7.0
" LICENSE:  MIT License "{{{
" Permission is hereby granted, free of charge, to any person obtaining a copy
" of this software and associated documentation files (the "Software"), to deal
" in the Software without restriction, including without limitation the rights
" to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
" copies of the Software, and to permit persons to whom the Software is
" furnished to do so, subject to the following conditions:
" 
" The above copyright notice and this permission notice shall be included in
" all copies or substantial portions of the Software.
" 
" THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
" IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
" FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
" AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
" LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
" OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
" THE SOFTWARE.
" }}}
"

let s:lib = {}

function! procpy#import()
  return s:lib
endfunction

function! s:lib.open(command)
    python proc = procpy()
    execute ":python proc.open('" . substitute(a:command, "'", "''", "g") . "')"
endfunction

" XXX - python needs to write to b:procpy_output
function! s:lib.read(timeout)
    let b:procpy_output = []
    execute ":python proc.read(" . string(a:timeout) . ")"
    return b:procpy_output
endfunction

function! s:lib.write(command)
    let l:cleaned = a:command
    " newlines between python and vim are a mess
    let l:cleaned = substitute(l:cleaned, '\n', '\\n', 'g')
    let l:cleaned = substitute(l:cleaned, '\r', '\\r', 'g')
    let l:cleaned = substitute(l:cleaned, "'", "''", 'g')
    execute ":python proc.write('" . l:cleaned . "')"
endfunction

python << EOF

# Heavily borrowed from vimsh.py <http://www.vim.org/scripts/script.php?script_id=165>
#
# TODO: Windows (popens)
# TODO: merge proc.c/vim into unified interface with procpy

import vim, sys, os, string, signal, re, time, pty, tty, select

class procpy:


    # constructor I guess (anything could be possible in python?)
    def __init__(self):
        self.buffer  = vim.current.buffer


    # create the pty or whatever
    def open(self, command):
        command_arr  = command.split()
        self.command = command_arr[0]
        self.args    = command_arr

        try:
            self.pid, self.fd = pty.fork()
        except:
            print "pty.fork() failed. Did you mean pty.spork() ???"

        # child proc, replace with command after fucking with terminal attributes
        if self.pid == 0:

            # set some attributes
            attrs = tty.tcgetattr( 1 )
            attrs[ 6 ][ tty.VMIN ]  = 1
            attrs[ 6 ][ tty.VTIME ] = 0
            attrs[ 0 ] = attrs[ 0 ] | tty.BRKINT
            attrs[ 0 ] = attrs[ 0 ] & tty.IGNBRK
            attrs[ 3 ] = attrs[ 3 ] | tty.ICANON | tty.ECHO | tty.ISIG
            tty.tcsetattr( 1, tty.TCSANOW, attrs )

            os.execv( self.command, self.args )

        # else master, pull termios settings and move on
        else:

            try:
                attrs = tty.tcgetattr( 1 )
                self.termios_keys = attrs[ 6 ]

            except:
                print  'setup_pty: tcgetattr failed. I guess <C-c> will have to work for you' 


    # read from pty
    # XXX - select.poll() doesn't work in OS X!!!!!!!
    def read(self, timeout = 0.1):

        output = ''

        # what, no do/while?
        while 1:
            s_read, s_write, s_error = select.select( [ self.fd ], [], [], timeout)

            lines = ''
            for s_fd in s_read:
                lines = os.read( self.fd, 32 )
                output = output + lines

            if lines == '':
                break

        #self.buffer.append(output)

        # XXX - BRUTAL
        lines_arr = re.split('\n', output)
        for v_line in lines_arr:
            command = 'call add(b:procpy_output, "' + re.sub('"', '""', v_line) + '")'
            vim.command(command)

        return 


    # I guess this one's not bad
    def write(self, command):
        os.write(self.fd, command)

    def kill(self):
        os.kill( self.pid, signal.SIGKILL )


EOF

