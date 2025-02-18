import curses
import json
from curses import wrapper
from curses.textpad import Textbox, rectangle

data = []
my_dict = {
    "LED 1": (1,2),
    "LED 2": (2,2),
    "FAN 1": (3,2),
    "FAN 2": (4,2),
    "TEMPERATURE" : (5,2),
    "HUMIDITY" : (6,2),
}
#VỊ TRÍ DATA[X][Y]
x = 0 
y = 0

text = 0
#ĐỌC FILE
def op_file():
    global data
    with open ("data_copy.txt","r") as file:
        data = json.load(file)

#GHI FILE
def write_file():
    with open ("data_copy.txt","w") as file:
        json.dump(data, file, indent=4)

#TẠO TEXTBOX
def text_box(stdscr):
    global text
   
    stdscr.addstr(19, 20, "CTRL+G KHI NHAP XONG ")
    win = curses.newwin(1, 30, 20, 20)  # Tạo cửa sổ con nhập dữ liệu
    rectangle(stdscr, 18, 19, 22, 51)  # Vẽ khung
    stdscr.refresh()

    box = Textbox(win)
    box.edit()  # Chỉnh sửa nội dung (Ctrl+G để xác nhận)
    
    text = box.gather().strip()  # Lấy nội dung nhập vào
   

    return text

#HIỂN THỊ YÊU CẦU
def title(stdscr,name):
    stdscr.addstr(17, 19, f"HÃY NHẬP {name} MUỐN SỬA ĐỔI")
    stdscr.refresh()

#HIỂN THỊ KẾT QUẢ NHẬP
def result(stdscr,text):
    stdscr.addstr(23,19 , f"Bạn đã nhập: {text}")
    stdscr.refresh()

#HIỂN THỊ THÔNG TIN
def show_table(stdscr):
    header = data[0]
    rectangle(stdscr, 1, 0, len(data) + 2, 50)
    for col,dat in enumerate(header):
        stdscr.addstr(2, (col+1)*12, f"{dat:<12}")

    infor = data[1:7]
    for cols,rows in enumerate(infor):
        for col1,row1 in enumerate(rows):
            stdscr.addstr(cols+3, (col1+1)*12, f"{row1:<12}")
    stdscr.refresh()

#XÁC ĐỊNH VỊ TRÍ DATADATA
def local_device(my_dict,text):
    global x,y
    x = my_dict[text][0]
    y = my_dict[text][1]

#CHECK TRẠNG THÁI CHO PHÉP DEVICE
def device_status():
    local_device(my_dict,text)
    a = int(my_dict[text][0])
    if a >=1 and a<=4:
        return 1
    else:
        return 2

def check_device(stdscr,text):
    list = ["LED 1", "LED 2", "FAN 1", "FAN 2", "TEMPERATURE", "HUMIDITY"]
    if text in list:
            return 1
    else:
            
        stdscr.addstr(17, 19,"THIẾT BỊ KHÔNG TỒN TẠI, HÃY NHẬP LẠI: ")
            
        stdscr.refresh()
        return 0
 


#GHI VÀO TRẠNG THÁI
def write(x,y,status):
    data[x][y] = status


def main(stdscr):
    global text
    op_file()
    stdscr.clear()
    while True:
        show_table(stdscr)
        title(stdscr,"THIẾT BỊ")
        text_box(stdscr)
        stdscr.refresh()
        while True:
            if check_device(stdscr,text) == 1:
                break
            else:
                text_box(stdscr)
        result(stdscr,text)
        stdscr.refresh()
        stdscr.getch()
        stdscr.clear()
        stdscr.refresh()
        i = device_status()
        if i == 1:
            show_table(stdscr)
            title(stdscr,"ON/OFF")
            text_box(stdscr)
            result(stdscr,text)
            write(x,y,text)
            write_file()
            show_table(stdscr)
            stdscr.refresh()
            stdscr.addstr(24,19 ,"NHAN Q NEU MUON THOAT CHUONG TRINH ")
            a = stdscr.getch()
            if a == ord("Q"):
                break
        else:
            show_table(stdscr)
            title(stdscr,"THÔNG SỐ HOẶC OFF")
            text_box(stdscr)
            result(stdscr,text)
            write(x,y,text)
            write_file()
            show_table(stdscr)
            stdscr.refresh()
            stdscr.addstr(24,19 ,"NHAN Q NEU MUON THOAT CHUONG TRINH ")
            a = stdscr.getch()
            if a == ord("Q"):
                break
        
wrapper(main)



















