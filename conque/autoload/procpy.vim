" beginning of python pty/popen library to share common interface with proc.c

function! procpy#open(command)
    execute ":python proc = procpy('" . a:command . "')"
    python proc.open()
endfnction

" XXX - python needs to write to l:output
function! procpy#read(timeout)
    let l:output = ''
    execute ":python proc.read(" . a:timeout. ")"
    return l:output
endfunction

function! procpy#write(command)
    execute ":python proc.write(" . a:command. ")"
endfunction

python << EOF

# Heavily borrowed from vimsh.py <http://www.vim.org/scripts/script.php?script_id=165>
#
# TODO: Windows (popens)
# TODO: merge proc.c/vim into unified interface with procpy

import vim, sys, os, string, signal, re, time, pty, tty, select

class procpy:


    # constructor I guess (anything could be possible in python?)
    def __init__( self, command ):
        command_arr  = command.split()
        self.command = command_arr[0]
        self.args    = command_arr
        self.buffer  = vim.current.buffer

        # sanity checks
        self._max_read_loops = 10


    # create the pty or whatever
    def open(self):
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
            attrs[ 3 ] = attrs[ 3 ] & ~tty.ICANON & ~tty.ECHO
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

        while 1:
            s_read, s_write, s_error = select.select( [ self.fd ], [], [], timeout)
            lines = ''

            for s_fd in s_read:
                lines = os.read( self.fd, 32 )
                output = output + lines

            if lines == '':
                break

        return output


    # I guess this ones not bad
    def write(self, command):
        os.write(self.fd, command)

    def kill(self):
        os.kill( self.pid, signal.SIGKILL )


test_ing = procpy('/bin/sh')
test_ing.open()
foo = test_ing.read(0.4)
test_ing.write("ls\n")
foo += test_ing.read(0.4)
test_ing.write("pwd\n")
foo += test_ing.read(0.4)
for ln in foo.split("\n"):
    test_ing.buffer.append(ln)
test_ing.kill()

EOF



