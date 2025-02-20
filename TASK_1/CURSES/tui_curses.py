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
    subwin = stdscr.subwin(4, 32, 18, 19)  # Tạo cửa sổ con 5x20 tại (10,10)
    subwin.clear()
    subwin.refresh()

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

    stdscr.addstr(17, 18, f"HÃY NHẬP {name} ")
    stdscr.refresh()

#HIỂN THỊ KẾT QUẢ NHẬP
def result(stdscr,text):
    stdscr.move(23, 0)  # Chọn dòng y
    stdscr.deleteln()
    stdscr.addstr(23,19 , f"Bạn đã nhập: {text} ")
    stdscr.refresh()

#HIỂN THỊ THÔNG TIN
def show_table(stdscr):
#MỖI LẦN GỌI HÀM THÌ TA SẼ XÓA ĐI BẢNGBẢNG CŨ VÀ KẾT THÚC BẰNG VIỆC GỌI HIỆN RA BẢNG MỚI
    subwin = stdscr.subwin(7, 30, 2, 4)  # Tạo cửa sổ con 5x20 tại (10,10)
    subwin.clear()
    subwin.refresh()


    rectangle(stdscr, 1, 0, len(data) + 2, 50)

    col_width = []
    for i in range(len(data[0])):
        max_row = 0
        for j in range(len(data)):
            if max_row < len(data[j][i]):
                max_row = len(data[j][i])
        col_width.append(max_row)

    

    for rows,value in enumerate(data):
        index = 0
        for col,vrow in enumerate(value):
            stdscr.addstr(rows+2, col_width[col-1]+index+4, f"{vrow}")
            index = col_width[col-1]+index+4
    stdscr.refresh()

#XÁC ĐỊNH VỊ TRÍ DATA
def local_device(my_dict,text):
    global x,y
    x = my_dict[text][0]
    y = my_dict[text][1]

#CHECK PHÂN LOẠI DEVICE
#NẾU LÀ 4 THIẾT BỊ BẬT TẮT THÌ TRẢ VỀ 1
#NẾU LÀ TEMP THÌ TRẢ VỀ 2
#NẾU LÀ HUMI THÌ TRẢ VỀ 33
def device_choose():
    local_device(my_dict,text)
    a = int(my_dict[text][0])
    if a >= 1 and a <= 4:
        return 1
    if a == 5:
        return 2
    if a == 6:
        return 3

def check_device(stdscr,text):
    list = ["LED 1", "LED 2", "FAN 1", "FAN 2", "TEMPERATURE", "HUMIDITY"]
    if text in list:
            return 1
    else:
            
        stdscr.addstr(17, 19,"THIẾT BỊ KHÔNG TỒN TẠI, HÃY NHẬP LẠI: ")   
        stdscr.refresh()
        return 0
 

def check_onoff(stdscr,text):
    
    if text == "ON" or text == "OFF":
        return 1
    else:
        stdscr.addstr(17, 19,"TRẠNG THÁI KHÔNG PHÙ HỢP, HÃY NHẬP LẠI: ")     
        stdscr.refresh()
        return 0

 
def check_humi(stdscr,text):
    num = int(text)
    if num <= 30 or num >= 90:

        stdscr.addstr(17, 19,"ĐỘ ẨM KHÔNG PHÙ HỢP, HÃY NHẬP LẠI: ")     
        stdscr.refresh()
        return 0
    else:
        return 1

def check_temp(stdscr,text):
    num = int(text)
    if num <= 16 or num >= 35:
        stdscr.addstr(17, 19,"NHIỆT ĐỘ KHÔNG PHÙ HỢP, HÃY NHẬP LẠI: ")     
        stdscr.refresh()
        return 0
    else:
        return 1
    



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
        i = device_choose()
        if i == 1:
            show_table(stdscr)
            title(stdscr,"ON/OFF")
           
            while True:
                text = text_box(stdscr)  # Chỉ gọi text_box(stdscr) một lần và gán vào text
                result(stdscr, text)  
                if check_onoff(stdscr, text) == 1:  # Dùng text đã nhập để kiểm tra
                    break  # Thoát vòng lặp nếu nhập đúng
            
            
            write(x,y,text)
            write_file()
            show_table(stdscr)
            stdscr.refresh()
            stdscr.addstr(24,19 ,"NHAN Q NEU MUON THOAT CHUONG TRINH ")
            a = stdscr.getch()
            if a == ord("Q"):
                break
            stdscr.move(24, 0)  # Chọn dòng y
            stdscr.deleteln()  # Xóa toàn bộ dòng hiện tại
            stdscr.move(23, 0)  # Chọn dòng y
            stdscr.deleteln()
            stdscr.refresh()
        
        if i == 2:
            show_table(stdscr)
            title(stdscr,"THÔNG SỐ HOẶC OFF")
           
            while True:
                text = text_box(stdscr)  # Chỉ gọi text_box(stdscr) một lần và gán vào text
                result(stdscr, text)  
                if check_temp(stdscr, text) == 1:  # Dùng text đã nhập để kiểm tra
                    break  # Thoát vòng lặp nếu nhập đúng

            
            write(x,y,text)
            write_file()
            show_table(stdscr)
            stdscr.refresh()
            stdscr.addstr(24,19 ,"NHAN Q NEU MUON THOAT CHUONG TRINH ")
            a = stdscr.getch()
            if a == ord("Q"):
                break
            stdscr.move(24, 0)  # Chọn dòng y
            stdscr.deleteln()  # Xóa toàn bộ dòng hiện tại
            stdscr.move(23, 0)  # Chọn dòng y
            stdscr.deleteln()
            stdscr.refresh()


        if i == 3:
            show_table(stdscr)
            title(stdscr,"THÔNG SỐ HOẶC OFF")
           
            while True:
                text = text_box(stdscr)  # Chỉ gọi text_box(stdscr) một lần và gán vào text
                result(stdscr, text)  
                if check_humi(stdscr, text) == 1:  # Dùng text đã nhập để kiểm tra
                    break  # Thoát vòng lặp nếu nhập đúng

            
            write(x,y,text)
            write_file()
            show_table(stdscr)
            stdscr.refresh()
            stdscr.addstr(24,19 ,"NHAN Q NEU MUON THOAT CHUONG TRINH ")
            a = stdscr.getch()
            if a == ord("Q"):
                break
            stdscr.move(24, 0)  # Chọn dòng y
            stdscr.deleteln()  # Xóa toàn bộ dòng hiện tại
            stdscr.move(23, 0)  # Chọn dòng y
            stdscr.deleteln()
            stdscr.refresh()









wrapper(main)



















