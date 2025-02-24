from prompt_toolkit import PromptSession
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
import json 

from tabulate import tabulate

from prompt_toolkit.shortcuts import message_dialog
from prompt_toolkit.shortcuts import input_dialog
from prompt_toolkit.shortcuts import yes_no_dialog
from prompt_toolkit.shortcuts import radiolist_dialog
from prompt_toolkit.shortcuts import checkboxlist_dialog

from prompt_toolkit.application import Application
from prompt_toolkit.layout import Layout
from prompt_toolkit.widgets import Button, Dialog, Label


                
#LẤY FILE TRẠNG THÁI CŨ
with open("data.txt", "r") as file:
    data = json.load(file)

table = tabulate(data, headers="firstrow", tablefmt="grid")


def choose_device():
    choose = radiolist_dialog(
        text = "BẠN MUỐN ĐIỀU CHỈNH GÌ",
        values = [
            ('L1','LED 1'),
            ('L2','LED 2'),
            ('F1','FAN 1'),
            ('F2','FAN 2'),
            ('temp','NHIỆT ĐỘ'),
            ('humi','ĐỘ ẨM')
        ]
    ).run()
    return choose

def set_status():
    sta = radiolist_dialog(
        text = "BẠN MUỐN BẬT HAY TẮT",
        values = [
            ('1','ON'),
            ('2','OFF')
        ]
    ).run()
    return sta


def adjust(str1,str2):
    set = input_dialog(
        title = str1,
        text = str2
    ).run()
    return set


def show_table():
    table = tabulate(data, headers="firstrow", tablefmt="grid")    
    message_dialog(
        title = "STATUS",
        text = table 
    ).run()

def escape():  
    result = yes_no_dialog(
        title='Xác nhận',
        text='Bạn có chắc chắn muốn tiếp tục?'
    ).run()
    return result

while True: 
    show_table()
    ext = int(escape())
    if ext == 0:
        break
    CHOOSE = choose_device()
    if CHOOSE == "L1":
        STAT = set_status()
        if STAT == "1":
            data[1][2] = "ON"
        else:
            data[1][2] = "OFF"
        
    if CHOOSE == "L2":
        STAT = set_status()
        if STAT == "1":
            data[2][2] = "ON"
        else:
            data[2][2] = "OFF"

    if CHOOSE == "F1":
        STAT = set_status()
        if STAT == "1":
            data[3][2] = "ON"
        else:
            data[3][2] = "OFF"

    if CHOOSE == "F2":
        STAT = set_status()
        if STAT == "1":
            data[4][2] = "ON"
        else:
            data[4][2] = "OFF"
        
    if CHOOSE == "temp":
        STAT = set_status()
        if STAT == "1":
            i = adjust("NHIET DO","HAY NHAP VAO NHIET DO: ")
            while True:
                if int(i) <= 16 or int(i)>=39:
                    i = adjust("NHIET DO KHONG HOP LE","HAY NHAP LAI NHIET DO: ")
                else:
                    break
            data[5][2] = i
        else:
            data[5][2] = "OFF"

    if CHOOSE == "humi":
        if STAT == "1":
            i = adjust("DO AM","HAY NHAP VAO DO AM: ")
            while True:
                if int(i) <= 30 or int(i) >= 90:
                    i = adjust("DO AM KHONG HOP LE","HAY NHAP LAI DO AM: ")
                else:
                    break
            data[6][2] = i
        else:
            data[6][2] = "OFF"
    with open("data.txt", "w") as file:
        json.dump(data, file, indent=4)