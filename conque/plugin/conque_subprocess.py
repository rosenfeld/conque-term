
###################################################################################################
class ConqueSubprocess:

    # constructor
    def __init__(self): # {{{
        self.pid = 0
        # }}}

    # create the pty or whatever (whatever == windows)
    def open(self, command, env = {}): # {{{
        command_arr  = command.split()
        self.command = command_arr[0]
        self.args    = command_arr

        try:
            self.pid, self.fd = pty.fork()
            logging.debug(self.pid)
        except:
            logging.debug("pty.fork() failed. Did you mean pty.spork() ???")

        # child proc, replace with command after altering terminal attributes
        if self.pid == 0:

            # set requested environment variables
            for k in env.keys():
                os.environ[k] = env[k]

            # set some attributes
            try:
                attrs = tty.tcgetattr(1)
                attrs[0] = attrs[0] ^ tty.IGNBRK
                attrs[0] = attrs[0] | tty.BRKINT | tty.IXANY | tty.IMAXBEL
                attrs[2] = attrs[2] | tty.HUPCL
                attrs[3] = attrs[3] | tty.ICANON | tty.ECHO | tty.ISIG | tty.ECHOKE
                attrs[6][tty.VMIN]  = 1
                attrs[6][tty.VTIME] = 0
                tty.tcsetattr(1, tty.TCSANOW, attrs)
            except:
                pass

            os.execvp(self.command, self.args)

        # else master, do nothing
        else:
            pass

        # }}}

    # read from pty
    # XXX - select.poll() doesn't work in OS X!!!!!!!
    def read(self, timeout = 1): # {{{

        output = ''
        read_timeout = float(timeout) / 1000

        # what, no do/while?
        while 1:
            s_read, s_write, s_error = select.select( [ self.fd ], [], [], read_timeout)

            lines = ''
            for s_fd in s_read:
                try:
                    lines = os.read( self.fd, 32 )
                except:
                    pass
                output = output + lines

            if lines == '':
                break

        return output
        # }}}

    # I guess this one's not bad
    def write(self, input): # {{{
        os.write(self.fd, input)
        # }}}

    # signal process
    def signal(self, signum): # {{{
        os.kill(self.pid, signum)
        # }}}

    # get process status
    def get_status(self): #{{{

        p_status = 1 # boooooooooooooooooogus

        try:
            if os.waitpid( self.pid, os.WNOHANG )[0]:
                p_status = 0
            else:
                p_status = 1
        except:
            p_status = 0

        command = 'let b:proc_py_status = ' + str(p_status)
        vim.command(command)
        # }}}

    # update window size in kernel, then send SIGWINCH to fg process
    def check_window_size(self): # {{{

        if self.window.width != self.columns or self.window.height != self.lines:
            # update instance properties
            self.columns = self.window.width
            self.lines = self.window.height
            self.working_columns = self.window.width
            self.working_lines = self.window.height

            # update window size in kernel
            try:
                fcntl.ioctl(self.fd, termios.TIOCSWINSZ, struct.pack("HHHH", self.lines, self.columns, 0, 0))
                os.kill(self.pid, signal.SIGWINCH)
            except:
                pass

        # }}}


