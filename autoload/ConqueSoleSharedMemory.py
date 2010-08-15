
import logging # DEBUG
LOG_FILENAME = 'pylog_sub.log' # DEBUG
#logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG) # DEBUG

import mmap

##############################################################
# shared memory creation

# XXX - not interested in learning Python reserved words, so everything is mem_

class ConqueSoleSharedMemory():

    # ****************************************************************************
    # class properties

    # {{{

    # is the data being stored not fixed length
    fixed_length = False

    # size of shared memory, in bytes / chars
    mem_size = None

    # size of shared memory, in bytes / chars
    mem_type = None

    # unique key, so multiple console instances are possible
    mem_key = None

    # mmap instance
    shm = None

    # }}}

    # ****************************************************************************
    # constructor I guess

    def __init__ (self, mem_size, mem_type, mem_key, fixed_length = False): # {{{

        self.mem_size = mem_size
        self.mem_type = mem_type
        self.mem_key  = mem_key
        self.fixed_length = fixed_length

    # }}}

    # ****************************************************************************
    # create memory block

    def create (self, access = 'write'): # {{{

        if access == 'write':
            mmap_access = mmap.ACCESS_WRITE
        else:
            mmap_access = mmap.ACCESS_READ

        name = "conque_%s_%s" % (self.mem_type, self.mem_key)

        self.shm = mmap.mmap (0, self.mem_size, name, mmap_access)

        if not self.shm:
            return False
        else:
            return True

        # }}}

    # ****************************************************************************
    # read data

    def read (self, chars = 1, start = 0): # {{{

        # invalid reads
        if chars == 0 or start + chars > self.mem_size:
            return ''

        # go to start position
        self.shm.seek(start)

        if not self.fixed_length:
            chars = self.shm.find(chr(0))

        shm_str = self.shm.read(chars).encode('ascii', '?')

        return shm_str

        # }}}

    # ****************************************************************************
    # write data

    def write(self, text, start = 0): # {{{

        self.shm.seek(start)

        if self.fixed_length:
            self.shm.write(text)
        else:
            self.shm.write(text + chr(0))

        # }}}

    # ****************************************************************************
    # clear

    def clear(self, start = 0): # {{{

        self.shm.seek(start)

        if self.fixed_length:
            self.shm.write(' ' * self.mem_size)
        else:
            self.shm.write(chr(0))

        # }}}


