
import logging # DEBUG
LOG_FILENAME = 'pylog_sub.log' # DEBUG
#logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG) # DEBUG

import mmap, pickle

##############################################################
# shared memory creation

# XXX - not interested in learning Python reserved words, so everything is mem_

class ConqueSoleSharedMemory():

    # ****************************************************************************
    # class properties

    # {{{

    # is the data being stored not fixed length
    fixed_length = False

    # fill memory with this character when clearing and fixed_length is true
    fill_char = ' '

    # serialize and unserialize data automatically
    serialize = False

    # size of shared memory, in bytes / chars
    mem_size = None

    # size of shared memory, in bytes / chars
    mem_type = None

    # unique key, so multiple console instances are possible
    mem_key = None

    # mmap instance
    shm = None

    # character encoding, dammit
    encoding = 'ascii'

    # }}}

    # ****************************************************************************
    # constructor I guess

    def __init__ (self, mem_size, mem_type, mem_key, fixed_length = False, fill_char = ' ', serialize = False, encoding = 'ascii'): # {{{

        self.mem_size = mem_size
        self.mem_type = mem_type
        self.mem_key  = mem_key
        self.fixed_length = fixed_length
        self.fill_char = fill_char
        self.serialize = serialize
        self.encoding = encoding

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
        if self.fixed_length and (chars == 0 or start + chars > self.mem_size):
            return ''

        # go to start position
        self.shm.seek(start)

        if not self.fixed_length:
            chars = self.shm.find(chr(0))

        shm_str = self.shm.read(chars)

        # encoding
        if self.encoding != 'ascii':
            try:
                shm_str = unicode(shm_str, self.encoding)
            except:
                pass

        if self.serialize and shm_str != '':
            try: 
                return pickle.loads(shm_str)
            except: 
                return ''
        else:
            return shm_str

        # }}}

    # ****************************************************************************
    # write data

    def write(self, text, start = 0): # {{{

        if self.serialize:
            tw = pickle.dumps(text, 0)
        else:
            tw = text

        self.shm.seek(start)
    
        # if it's not ascii, it's probably some unicode disaster
        if self.encoding != 'ascii':
            
            # first, ensure string is a unicode object
            try:
                twu = unicode(tw, self.encoding)
            except:
                twu = tw

            # then encode it into bytes that are friendly to mmap
            twm = twu.encode(self.encoding, 'replace')

        # if ascii, then do nothing
        else:
            twm = tw.encode('ascii', 'replace')

        # write to memory
        if self.fixed_length:
            self.shm.write(twm)
        else:
            self.shm.write(twm + chr(0))

        # }}}

    # ****************************************************************************
    # clear

    def clear(self, start = 0): # {{{

        self.shm.seek(start)

        if self.fixed_length:
            self.shm.write(self.fill_char * self.mem_size)
        else:
            self.shm.write(chr(0))

        # }}}

    # ****************************************************************************
    # close

    def close(self):

        self.shm.close()


