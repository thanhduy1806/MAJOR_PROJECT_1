import curses
from curses.textpad import rectangle

data = [
    ["ID", "Tên", "Tuổi", "Điể"],
    ["1", "An", "20", "8.5"],
    ["2", "Bình", "22", "7.8"],
    ["3", "Cường", "19", "9.1"],
]

def show_table(stdscr):
    stdscr.clear()
    stdscr.addstr(0, 0, "Bảng Thông Tin", curses.A_BOLD)

    # Vẽ khung ngoài
    rectangle(stdscr, 1, 0, len(data) + 2, 50)

    # Hiển thị dữ liệu
    for row_idx, row in enumerate(data):
        for col_idx, col in enumerate(row):
            stdscr.addstr(row_idx + 2, col_idx * 12 + 2, f"{col:<12}")  # Canh trái

    stdscr.refresh()
    stdscr.getch()

curses.wrapper(show_table)
