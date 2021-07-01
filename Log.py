# coding=utf-8
import os
from datetime import datetime
import DATA as DATA

def write_to_log(file_name,user,code,text):
    """Write into the log
    
    Arguments:
        file_name {string} -- Name of the log file
        user {string} -- User to write the log
        code {string} -- Code of the type of log text
        text {string} -- Text to write in log
    """

    try:
        checkPath()
        name = os.path.join(DATA.LOG_PATH,(file_name + "__" + DATA.LOG_PATH_LOG))
        with open(name, 'a+') as file:
            file.write("["+str(datetime.now())+"]("+(str(code) if code != None else "NULL")+"){"+(str(user) if user != None else "NULL")+"} --> " + (str(text) if text != None else "NULL") + "\n")

    except Exception as e:
        print(str(e))

def checkPath():
    if not os.path.exists(DATA.LOG_PATH): os.makedirs(DATA.LOG_PATH,mode=0o777, exist_ok=True)