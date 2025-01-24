import wmi
from logger import write_log

PROGRAM = "main.exe"
def execute_application(STARTUP_PATH):
    import subprocess
    try:
        subprocess.Popen([STARTUP_PATH + '\\main.exe'], shell=True)
        write_log("Process is started.")
    except Exception as e:
        write_log(e, 'exception')

def check_and_kill_process():
    wmiObj = wmi.WMI()

    result = {}

    for process in wmiObj.Win32_Process():
        if PROGRAM == process.Name.lower():
            write_log(PROGRAM + " is executing... with pid: " +str(process.ProcessId))
            stop_the_process(process.ProcessId)

    return result

def stop_the_process(process_id):
    import os
    try:
        os.system('taskkill /F /PID ' +str(process_id))
        write_log("Old process was killed.")
    except Exception as e:
        write_log(e, 'exception')