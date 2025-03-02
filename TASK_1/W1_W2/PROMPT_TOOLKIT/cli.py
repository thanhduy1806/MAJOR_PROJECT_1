from prompt_toolkit import PromptSession
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
import json 
session = PromptSession()

#TẠO DATA LÀ BIẾN TOÀN CỤC
data = []

#TẠO CÁC GỢI Ý 
devices = ["LED 1", "LED 2", "Fan 1", "Fan 2"]
device_completer = WordCompleter(devices, ignore_case=True)

stat = ["ON", "OFF"]
stat_completer = WordCompleter(stat, ignore_case=True)

ext = ["exit"]
ext_completer = WordCompleter(ext, ignore_case=True)

#TẠO MÀU SẮC
cli_style = Style.from_dict({
    "prompt" : "ansiblue",
    "answer" : "ansiyellow",
    "completion.current" : "ansigreen"
})

#LẤY FILE TRẠNG THÁI CŨ
with open("data.txt", "r") as file:
    data = json.load(file)

#HIỂN THỊ BẢNG
def display_table():
    global data
    #Tìm độ rộng lớn nhất cho cộtcột
    col_width = []
    for i in range(len(data[0])):
        max_row = 0
        for j in range(len(data)):
            if max_row < len(data[j][i]):
                max_row = len(data[j][i])
        col_width.append(max_row)     

    
    print("-"*25)
    for row in data:
        format_row =  (row[i].ljust(col_width[i]) for i in range(len(row)))
        print("|" + " | ".join(format_row) + "|")
        print("-"*25)

#CÁC TRƯỜNG HỢP ĐIỀU KHIỂN
def option():
    global data
    global session
   
    option = session.prompt("ENTER 'Q' TO SELECT OR 'A' TO SET ALL ", style=cli_style)
    while True:
        if option == "A":
            option_A = prompt("SET STATUS FOR ALL DEVICE ",completer=stat_completer, style=cli_style)
            if option_A == "ON":
                for i in range(1,5):
                    data[i][2] = "ON"
            else:
                for i in range(1,5):
                    data[i][2] = "OFF"

        if option == "Q":
            name = session.prompt("ENTER YOUR NAME OF DEVICE ",completer=device_completer, style=cli_style)
            status = session.prompt("SET UP STATUS ",completer=stat_completer, style=cli_style)
            if name == "LED 1":
                if status == "ON":
                    data[1][2] = "ON"
                else:
                    data[1][2] = "OFF"

            if name == "LED 2" :
                if status == "ON":
                    data[2][2] = "ON"
                else:
                    data[2][2] = "OFF"

            if name == "Fan 1" :
                if status == "ON":
                    data[3][2] = "ON"
                else:
                    data[3][2] = "OFF"

            if name == "Fan 2" :
                if status == "ON":
                    data[4][2] = "ON"
                else:
                    data[4][2] = "OFF"

        cont = session.prompt("ENTER C TO CONTINUE OR S TO STOP ")
        if cont == "C" or cont == "c":
            continue
        else:
            with open("data.txt", "w") as file:
                json.dump(data, file, indent=4)
                break
    print("\033[32mCOMPLETELY!...\033[0m")
   

if __name__ == '__main__':
    print("WELL COME TO CONTROL TABLE ")
    while True:
        try:
            print("VIEWING OR SETTING")
            print("Press 1 to view")
            print("Press 2 to set")
            print("Crt+D to escape")
            init = session.prompt("enter ")
        except EOFError:
            break 
        if init == "1":
            display_table()
            while True:
                user_input = input("Nhập 'E' để thoát: ")
                if user_input == "E":
                    print("Thoát chế độ view!")
                    break  
        if init == "2":
            display_table()
            option()
            display_table()
            while True:
                user_input = input("Nhập 'E' để thoát: ")
                if user_input == "E":
                    print("Thoát chế độ setting!")
                    break