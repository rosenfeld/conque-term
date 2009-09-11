" FILE:     autoload/subprocess/proc_py.vim
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

function! subprocess#proc_py#import() "{{{
  return s:lib
endfunction "}}}

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" API methods

function! s:lib.open(command) "{{{
    python proc = proc_py()
    execute ":python proc.open('" . s:python_escape(a:command) . "')"
endfunction "}}}

function! s:lib.read(...) "{{{
    let timeout = get(a:000, 0, 0.2)
    let b:proc_py_output = []
    execute ":python proc.read(" . string(timeout) . ")"
    return b:proc_py_output
endfunction "}}}

function! s:lib.write(command) "{{{
    execute ":python proc.write('" . s:python_escape(a:command) . "')"
endfunction "}}}

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Util

function! s:python_escape(str_in) "{{{
    let l:cleaned = a:str_in
    " newlines between python and vim are a mess
    let l:cleaned = substitute(l:cleaned, '\\', '\\\\', 'g')
    let l:cleaned = substitute(l:cleaned, '\n', '\\n', 'g')
    let l:cleaned = substitute(l:cleaned, '\r', '\\r', 'g')
    let l:cleaned = substitute(l:cleaned, "'", "''", 'g')
    return l:cleaned
endfunction "}}}

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Python {{{
python << EOF

# Subprocess management in python.
# Uses 'pty' when possible 'popen' otherwise.
# 
# TODO: Beat interactive Windows commands into submission.
# TODO: Investigate win32pipe
#
# Heavily borrowed from vimsh.py <http://www.vim.org/scripts/script.php?script_id=165>

import vim, sys, os, string, signal, re, time

if sys.platform == 'win32' or sys.platform == 'win64':
    import popen2, stat
    use_pty = 0
else:
    import pty, tty, select
    use_pty = 1


class proc_py:


    # constructor I guess (anything could be possible in python?)
    def __init__(self):
        self.buffer  = vim.current.buffer


    # create the pty or whatever (whatever == windows)
    def open(self, command):
        command_arr  = command.split()
        self.command = command_arr[0]
        self.args    = command_arr

        # pty: praise jesus!
        if use_pty:

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

        # no pty, dagnabit
        else:
            # apparently pipes > popen2
            try:
                import win32pipe
                self.stdin, self.stdout, self.stderr = win32pipe.popen3(command)

            except ImportError:
                print 'w32 === fail!' # this always fails for me
                self.stdout, self.stdin, self.stderr = popen2.popen3(command, -1, 'b')

            self.outd = self.stdout.fileno()
            self.ind  = self.stdin.fileno ()
            self.errd = self.stderr.fileno()


    # read from pty
    # XXX - select.poll() doesn't work in OS X!!!!!!!
    def read(self, timeout = 0.1):

        output = ''

        # score
        if use_pty:

            # what, no do/while?
            while 1:
                s_read, s_write, s_error = select.select( [ self.fd ], [], [], timeout)

                lines = ''
                for s_fd in s_read:
                    lines = os.read( self.fd, 32 )
                    output = output + lines

                if lines == '':
                    break

        # urk, windows
        else: 
            time.sleep(timeout)

            count = 0
            count = os.fstat(self.outd)[stat.ST_SIZE]

            while (count > 0):

                tmp = os.read(self.outd, 1)
                output += tmp

                count = os.fstat(self.outd)[stat.ST_SIZE]

                if len(tmp) == 0:
                    break


        # XXX - BRUTAL
        lines_arr = re.split('\n', output)
        for v_line in lines_arr:
            cleaned = v_line
            cleaned = re.sub('\\\\', '\\\\\\\\', cleaned) # ftw!
            cleaned = re.sub('"', '""', cleaned)
            command = 'call add(b:proc_py_output, "' + cleaned + '")'
            vim.command(command)

        return 


    # I guess this one's not bad
    def write(self, command):
        if use_pty:
            os.write(self.fd, command)
        else:
            os.write(self.ind, command)

    def kill(self):
        if use_pty:
            os.kill( self.pid, signal.SIGKILL )
        else:
            os.close(self.ind)
            os.close(self.outd)
            os.close(self.errd)



EOF

"}}}

