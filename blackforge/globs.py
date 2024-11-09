import os, sys
from itertools import count
import re, random, time, datetime, ctypes
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = str(True)
import pygame as pg
import numpy as np, moderngl as mgl, glm, glfw


_blackforge_dir_:str = __file__.removesuffix(f"{__name__.split(".")[1]}.py")

def _setConsoleTextAttr(color):
    if sys.platform == "win32":
        console_handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32. SetConsoleTextAttribute(console_handle, color)
    else:
        if color == 7:
            print("\u001b[0m", end = "", flush = True)

        elif color == 13:
            print("\u001b[31;1m", end = "", flush = True)

        elif color == 12:
            print("\u001b[31m", end = "", flush = True)

        else:
            ...

class Logger:
    DUMP_AT:int=8

    LOG_NONE:int=-1
    LOG_INFO:int=0
    LOG_WARNING:int=1
    LOG_ERROR:int=2
    LOG_FATAL:int=3
    LOG_SYSTEM:int=4

    def __init__(self):
        self.dumptime:float=0.0
        """ time since last dump """

        self.dump:bool=False
        """ flag to control when the logger dumps logs to the stdout """
        
        self.text = ""
        self.info_level = {
            self.LOG_INFO: "INFO",
            self.LOG_WARNING: "WARNING",
            self.LOG_ERROR: "ERROR",
            self.LOG_FATAL: "FATAL",
            self.LOG_SYSTEM: "SYSTEM"
        }
        self.info_color = {
            self.LOG_INFO: 3,
            self.LOG_WARNING: 6,
            self.LOG_ERROR: 1,
            self.LOG_FATAL: 0,
            self.LOG_SYSTEM: 10
        }

    def log(self, level, msg):
        stamp =  datetime.datetime.now().strftime("[%m/%d/%Y-%H:%M:%S]")
        self.text += datetime.datetime.now().strftime("[%m/%d/%Y-%H:%M:%S]") + f": BlackForge: %s: %s" % ({self.LOG_INFO: "info", self.LOG_WARNING: "warning", self.LOG_ERROR: "error", self.LOG_FATAL: "fatal error", self.LOG_SYSTEM: "system info"}[level], msg) + "\n"
        
        if level > self.LOG_NONE: #and self.dump:
            _setConsoleTextAttr(5)
            print(f"{stamp} ", end = "", flush = True)
            _setConsoleTextAttr(7)
            print("BlackForge: ", end = "", flush = True)
            _setConsoleTextAttr(self.info_color[level])
            print("%s: " % self.info_level[level], end = "", flush = True)
            _setConsoleTextAttr(self.info_color[level])
            print(f"{msg}\n")
            _setConsoleTextAttr(7)
    
    def fixedLog(self, level, msg):
        stamp =  datetime.datetime.now().strftime("[%m/%d/%Y-%H:%M:%S]")
        self.text += datetime.datetime.now().strftime("[%m/%d/%Y-%H:%M:%S]") + f": BlackForge: %s: %s" % ({self.LOG_INFO: "info", self.LOG_WARNING: "warning", self.LOG_ERROR: "error", self.LOG_FATAL: "fatal error", self.LOG_SYSTEM: "system info"}[level], msg) + "\n"
        
        if level > self.LOG_NONE and self.dump:
            _setConsoleTextAttr(5)
            print(f"FIXED LOG :: {stamp} ", end = "", flush = True)
            _setConsoleTextAttr(7)
            print("BlackForge: ", end = "", flush = True)
            _setConsoleTextAttr(self.info_color[level])
            print("%s: " % self.info_level[level], end = "", flush = True)
            _setConsoleTextAttr(self.info_color[level])
            print(f"{msg}\n")
            _setConsoleTextAttr(7)

    def get(self):
        return self.text

    def save(self, filePath):
        with open(filePath, "w") as file:
            file.write(self.text)

    def update(self, dt:float) -> None:
        if int(self.dumptime) == self.DUMP_AT:
            self.dump = True
            self.dumptime = 0.0
        else: 
            self.dump = False
            self.dumptime+=dt
_logger = Logger()

