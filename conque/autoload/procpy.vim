" beginning of python pty/popen library to share common interface with proc.c

function! procpy#test()
    call procpy#open('/bin/bash')
    call append(line('$'), procpy#read(0.2))

    call procpy#write("stty -a\n")
    call append(line('$'), procpy#read(0.2))

    call procpy#write("cd ~/.vi\t")
    call append(line('$'), procpy#read(0.2))

    call procpy#write("/autoload\n")
    call append(line('$'), procpy#read(0.2))

    call procpy#write("pwd\n")
    call append(line('$'), procpy#read(0.2))
endfunction

function! procpy#open(command)
    execute ":python proc = procpy('" . substitute(a:command, "'", "''", "g") . "')"
    python proc.open()
endfunction

" XXX - python needs to write to l:output
function! procpy#read(timeout)
    let b:procpy_output = []
    execute ":python proc.read(" . string(a:timeout) . ")"
    return b:procpy_output
endfunction

function! procpy#write(command)
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


    # I guess this ones not bad
    def write(self, command):
        os.write(self.fd, command)

    def kill(self):
        os.kill( self.pid, signal.SIGKILL )


EOF

