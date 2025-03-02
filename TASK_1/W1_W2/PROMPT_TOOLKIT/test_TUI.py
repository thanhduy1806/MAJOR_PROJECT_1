import os
import json
import threading
import time
from prompt_toolkit import Application
from prompt_toolkit.layout import Layout, HSplit, VSplit, Window, FormattedTextControl, WindowAlign
from prompt_toolkit.widgets import Frame, TextArea
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from datetime import datetime
import pytz
import psutil

# 📌 Tạo nội dung trong LOGS
logs_content = Label("Logs Settings:\n\nLog Level: INFO\nErrors: 0", style="fg:green")

# 🖼️ Tạo FRAME Logs chính
logs_window = Frame(
    body=logs_content, 
    title="Logs",
    width=50,
    height=15
)

# 🖼️ Tạo một FRAME CON trong ô LOGS
sub_window = Frame(
    body="Sub-Log Window",
    title="Sub-Logs", 
    width=30,
    height=5
)

# 📌 FloatContainer để đặt sub_window vào logs
logs_container = FloatContainer(
    content=logs_window,  # Cửa sổ Logs chính
    floats=[
        Float(content=sub_window, left=5, top=4)  # Đặt sub_window vào trong logs
    ]
)

# 🖥️ Layout chính
layout = Layout(logs_container)

# 🚀 Tạo ứng dụng Prompt Toolkit
app = Application(layout=layout, full_screen=True)

# 🏃‍♂️ Chạy ứng dụng
app.run()
