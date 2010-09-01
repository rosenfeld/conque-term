"""
Python structures used for ctypes interaction
"""

from ctypes import *
from ctypes.wintypes import BOOL

# types with variable names comparable to win32 documentation

BYTE = c_ubyte
WORD = c_ushort
DWORD = c_ulong
LPBYTE = POINTER(c_ubyte)
LPTSTR = POINTER(c_char) 
HANDLE = c_void_p
PVOID = c_void_p
LPVOID = c_void_p
UNIT_PTR = c_ulong
SIZE_T = c_ulong

# create process flag constants

CREATE_BREAKAWAY_FROM_JOB = 0x01000000
CREATE_DEFAULT_ERROR_MODE = 0x04000000
CREATE_NEW_CONSOLE = 0x00000010
CREATE_NEW_PROCESS_GROUP = 0x00000200
CREATE_NO_WINDOW = 0x08000000
CREATE_PROTECTED_PROCESS = 0x00040000
CREATE_PRESERVE_CODE_AUTHZ_LEVEL = 0x02000000
CREATE_SEPARATE_WOW_VDM = 0x00000800
CREATE_SHARED_WOW_VDM = 0x00001000
CREATE_SUSPENDED = 0x00000004
CREATE_UNICODE_ENVIRONMENT = 0x00000400
DEBUG_ONLY_THIS_PROCESS = 0x00000002
DEBUG_PROCESS = 0x00000001
DETACHED_PROCESS = 0x00000008
EXTENDED_STARTUPINFO_PRESENT = 0x00080000
INHERIT_PARENT_AFFINITY = 0x00010000

# process priority constants

ABOVE_NORMAL_PRIORITY_CLASS = 0x00008000
BELOW_NORMAL_PRIORITY_CLASS = 0x00004000
HIGH_PRIORITY_CLASS = 0x00000080
IDLE_PRIORITY_CLASS = 0x00000040
NORMAL_PRIORITY_CLASS = 0x00000020
REALTIME_PRIORITY_CLASS = 0x00000100

# startup info constants

STARTF_FORCEONFEEDBACK = 0x00000040
STARTF_FORCEOFFFEEDBACK = 0x00000080
STARTF_PREVENTPINNING = 0x00002000
STARTF_RUNFULLSCREEN = 0x00000020
STARTF_TITLEISAPPID = 0x00001000
STARTF_TITLEISLINKNAME = 0x00000800
STARTF_USECOUNTCHARS = 0x00000008
STARTF_USEFILLATTRIBUTE = 0x00000010
STARTF_USEHOTKEY = 0x00000200
STARTF_USEPOSITION = 0x00000004
STARTF_USESHOWWINDOW = 0x00000001
STARTF_USESIZE = 0x00000002
STARTF_USESTDHANDLES = 0x00000100

# show window constants

SW_FORCEMINIMIZE = 11
SW_HIDE = 0
SW_MAXIMIZE = 3
SW_MINIMIZE = 6
SW_RESTORE = 9
SW_SHOW = 5
SW_SHOWDEFAULT = 10
SW_SHOWMAXIMIZED = 3
SW_SHOWMINIMIZED = 2
SW_SHOWMINNOACTIVE = 7
SW_SHOWNA = 8
SW_SHOWNOACTIVATE = 4
SW_SHOWNORMAL = 1


# structures used for CreateProcess

class STARTUPINFO(Structure):
    _fields_ = [("cb",            DWORD),        
                ("lpReserved",    LPTSTR), 
                ("lpDesktop",     LPTSTR),  
                ("lpTitle",       LPTSTR),
                ("dwX",           DWORD),
                ("dwY",           DWORD),
                ("dwXSize",       DWORD),
                ("dwYSize",       DWORD),
                ("dwXCountChars", DWORD),
                ("dwYCountChars", DWORD),
                ("dwFillAttribute",DWORD),
                ("dwFlags",       DWORD),
                ("wShowWindow",   WORD),
                ("cbReserved2",   WORD),
                ("lpReserved2",   LPBYTE),
                ("hStdInput",     HANDLE),
                ("hStdOutput",    HANDLE),
                ("hStdError",     HANDLE),]

class PROCESS_INFORMATION(Structure):
    _fields_ = [("hProcess",    HANDLE),
                ("hThread",     HANDLE),
                ("dwProcessId", DWORD),
                ("dwThreadId",  DWORD),]

class MEMORY_BASIC_INFORMATION(Structure):
    _fields_ = [("BaseAddress", PVOID),
                ("AllocationBase", PVOID),
                ("AllocationProtect", DWORD),
                ("RegionSize", SIZE_T),
                ("State", DWORD),
                ("Protect", DWORD),
                ("Type", DWORD),]

class SECURITY_ATTRIBUTES(Structure):
    _fields_ = [("Length", DWORD),
                ("SecDescriptor", LPVOID),
                ("InheritHandle", BOOL)]


