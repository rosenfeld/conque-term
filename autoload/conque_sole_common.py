
import mmap

##############################################################
# shared memory creation

# size of shared memory
SHM_SIZE = 4096

def create_shm (name, access):
    global SHM_SIZE
    name = "%s_%s" % ('conque_sole', name)
    smo = mmap.mmap (0, SHM_SIZE, name, access)
    if not smo:
        exit()
    else:
        return smo

def read_shm (shm):
    global SHM_SIZE
    shm.seek(0)
    shm_str = str(shm.read(SHM_SIZE)).rstrip(chr(0))
    return shm_str

def clear_shm(shm):
    global SHM_SIZE
    shm.seek(0)
    shm.write(chr(0) * SHM_SIZE)

def write_shm(shm, text):
    global SHM_SIZE
    shm.seek(0)
    shm.write(text + chr(0) * (SHM_SIZE - len(text)))

