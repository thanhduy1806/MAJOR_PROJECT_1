import curses

def main1(stdscr):
    curses.curs_set(1)  # Hiện con trỏ
    stdscr.addstr(1, 1, "Nhập chữ cái đầu tiên:")
    
    suggestions = ["apple", "alle", "apci", "banana", "ben", "bani", 
                   "grape", "gior", "gen", "mango", "mile", 
                   "orange", "outsti", "ohio", "ohirm"]

    user_input = ""  # Chuỗi người nhập
    matches = []  # Danh sách gợi ý
    selected_index = 0  # Chỉ mục gợi ý hiện tại

    while True:
        key = stdscr.getch()  # Lấy phím từ bàn phím

        if key == 10:  # Nhấn Enter -> Chọn từ gợi ý
            if matches:
                user_input = matches[selected_index]  # Chọn từ hiện tại
            break
        elif key == 9:  # Nhấn Tab -> Chuyển gợi ý tiếp theo
            if matches:
                selected_index = (selected_index + 1) % len(matches)
        elif 32 <= key <= 126:  # Nhập ký tự mới
            user_input = chr(key)  # Chỉ lấy chữ cái đầu tiên
            matches = [word for word in suggestions if word.startswith(user_input)]
            selected_index = 0  # Reset gợi ý về phần tử đầu
        elif key == 127 or key == curses.KEY_BACKSPACE:  # Xóa
            user_input = ""
            matches = []
            selected_index = 0

        # Hiển thị từ đang chọn
        stdscr.move(3, 1)
        stdscr.clrtoeol()
        stdscr.addstr(3, 1, f"Từ gợi ý: {matches[selected_index] if matches else 'Không có gợi ý'}")

        stdscr.refresh()

    stdscr.addstr(5, 1, f"Bạn đã chọn: {user_input if user_input else 'Không chọn'}")
    stdscr.refresh()
    stdscr.getch()









def autofill(stdscr):
    list = ["LED 1", "LED 2", "FAN 1","FAN 2", "TEMPERATURE", "HUMIDITY"]
    fill_list = []
    index = 0
    user_input = " "

    while True:
        char = stdscr.getch()
        if char == 10:
            user_output = fill_list[index]
            break
        if char == 9:
            index = (index+1) % len(fill_list)

        if 32 <= char <= 126:
            user_input = chr(char)
            fill_list = [word for word in list if word.upper().startswith(user_input.upper())]
            index = 0

        stdscr.move(3,1)
        stdscr.clrtoeol()
        stdscr.addstr(3,1,f"TỪ GỢI Ý {fill_list[index]}")

    stdscr.move(3,1)
    stdscr.clrtoeol()
    stdscr.addstr(3,1,f"BAN DA CHON {user_output}")
    return user_output


def main22(stdscr):
    curses.curs_set(1)  # Hiện con trỏ
    stdscr.addstr(1, 1, "Nhập chữ cái đầu tiên: ")
    autofill(stdscr)
    stdscr.refresh()
    stdscr.getch()








import curses
from curses.textpad import Textbox, rectangle

def main(stdscr):
    curses.curs_set(1)  # Hiển thị con trỏ nhập liệu
    stdscr.clear()

    # Danh sách gợi ý
    suggestions = ["apple", "alle", "apci", "banana", "ben", "bani",
                   "grape", "gior", "gen", "mango", "mile", "orange",
                   "outsti", "ohio", "ohirm"]

    # Vẽ textbox
    stdscr.addstr(1, 1, "Nhập từ:")
    rectangle(stdscr, 2, 1, 4, 30)  # (y1, x1, y2, x2)
    
    editwin = curses.newwin(1, 28, 3, 2)  # Ô nhập
    box = Textbox(editwin, insert_mode=True)

    user_input = ""  # Lưu trữ ký tự đã nhập
    selected_index = 0  # Vị trí gợi ý được chọn

    while True:
        stdscr.refresh()
        editwin.refresh()
        char = stdscr.getch()

        if char == 10:  # Nhấn Enter để chọn
            break
        elif char == 9:  # Nhấn Tab để duyệt gợi ý
            matches = [word for word in suggestions if word.lower().startswith(user_input.lower())]
            if matches:
                selected_index = (selected_index + 1) % len(matches)  # Duyệt qua danh sách
                user_input = matches[selected_index]  # Chọn từ gợi ý
                editwin.clear()
                editwin.addstr(0, 0, user_input)
                editwin.refresh()
        elif char == 263:  # Backspace (Xóa ký tự)
            user_input = user_input[:-1]
            box.do_command(char)
        else:
            user_input += chr(char)
            box.do_command(char)

        # Cập nhật Textbox để hiển thị ký tự đã nhập
        editwin.clear()
        editwin.addstr(0, 0, user_input)
        editwin.refresh()

    stdscr.addstr(6, 1, f"Bạn đã chọn: {user_input}")
    stdscr.getch()  # Đợi nhấn phím trước khi thoát

curses.wrapper(main)





