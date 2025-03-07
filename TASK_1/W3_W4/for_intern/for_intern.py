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
from prompt_toolkit.layout.containers import Window
import pytz
import psutil
import re
from tabulate import tabulate

class RaspiGUI:

    def __init__(self):
        self.sensor_value = [[None]*6 for _ in range(6)]
        self.output_log_line = [0,0,0,0,0,0]
        self.port_buffer = None
        self.formatted = []
        self.kb = KeyBindings()
        self.mode = 'menu'
        self.selected_item = 0
       
        self.container = self.get_container()

        self.text_from_command = "NO VALUE"

        self.selected_info = 0
        self.data_input_log = 0
        self.menu_items = [
            "────────────────",
            "  Status    ",
            "────────────────",
            " SControl  ",
             "────────────────",
            " Tracking ",
             "────────────────",
            "Dashboards",
             "────────────────",
            "   Logs   ",
             "────────────────",
            "  Option  ",
             "────────────────",
            "   Quit    ",
            "────────────────"
        ]
        
        self.settings_data = {}
        
        default_data = {
            "Status": [
                {"key": "CPU Usage", "value": f"{psutil.cpu_percent()}%"},
                {"key": "Memory Usage", "value": f"{psutil.virtual_memory().percent}%"},
                {"key": "Disk Usage", "value": f"{psutil.disk_usage('/').percent}%"},
                {"key": "Temperature", "value": f"{self.get_cpu_temperature()}°C"}
            ],
            "SControl": [
                {"key": "SSH Service", "value": "Enabled"},
                {"key": "VNC Service", "value": "Disabled"},
                {"key": "Remote GPIO", "value": "Enabled"},
                {"key": "Serial Port", "value": "Disabled"},
                {"key": "Port", "value": "8880"}
            ],
            "Tracking": [
                {"key": "GPS", "value": "Active"},
                {"key": "Last Update", "value": self.get_datetime()}
            ],
            "Dashboards": [
                {"key": "Users", "value": "150"},
                {"key": "Sessions", "value": "345"}
            ],
            "Logs": [
                {"key": "Log Level", "value": "INFO"},
                {"key": "Errors", "value": "0"}
            ],
            "Option": [
                {"key": "Language", "value": "Vietnamese"},
                {"key": "Theme", "value": "Dark"}
            ],
            "Quit": (
                "SpaceLiinTech\n"
                "[Project: BEE-PC1]\n"
                "[2025]\n"
            )
        }

        self.menu_list = ["Status","SControl","Tracking","Dashboards","Logs","Option","Quit"]

        self.style = Style.from_dict({
            'window': 'bg:#333333 #ffffff',
            'frame.border': '#FFFFBB',
            'frame.label':'#FFA500',
            'sizeframe.border': '#1313c2',   
            'datetimeframe.border': '#FF00FF',  
            'statusframe.border': '#00FF00',  
            'title': 'bold #00ff00',
            'menu.item': '#ffffff',
            'menu.selected': 'reverse',
            'info.title': 'bold #00ff00',
            'info.selected': 'reverse',
            'key': '#00ff00',
            'value': '#ffffff',
            'log': '#00ff00',
            'status': '#888888',
            'raspberry.red': '#ff0000',
            'raspberry.green': '#00ff00',     
        })
        

        categories = ["Status", "SControl", "Tracking", "Dashboards", "Logs", "Option", "Quit"]
        for cat in categories:
            filename = f"{cat}.json"
            self.settings_data[cat] = self.load_category_data(filename, default_data[cat])
            #Hàm này để load từ các file.json vào list self.settings_data, tên các file json cũng ứng với danh mục trong categories
            #self.settings_data lưu dưới dạng các dict lồng nhau

        self.utils_data = {
            "timestamp": "unknown",
            "cpu_usage": 0,
            "memory_usage": 0,
            "disk_usage": 0,
            "temperature": 0
        }
        self.setup_keybindings()

        threading.Thread(target=self.update_utils_data, daemon=True).start()

        
        
        #TẠO LUỒNG ĐỂ CHẠY THỜI GIAN
        time_thread = threading.Thread(target=self.load_time, daemon=True)
        time_thread.start()

        #TẠO LUỒNG UPDATE VALUE SENSOR
        sensor_thread = threading.Thread(target= self.send_to_matrix, daemon=True)
        sensor_thread.start()

    #TAO 1 LUONG DE LIEN TUC UPDATE THOI GIAN 
    def load_time(self):
        while True:
            self.utils_data["timestamp"]=datetime.now().strftime("%d/%m/%Y,%H:%M:%S")
            with open("time.txt","w") as file:
                file.write(datetime.now().strftime("%d/%m/%Y,%H:%M:%S"))
            time.sleep(1)
    



    def load_category_data(self, filename, default_data):
        if not os.path.exists(filename):
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(default_data, f, indent=4, ensure_ascii=False)
            except Exception as e:
                print(f"Error writing {filename}: {e}")
            return default_data
        else:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                return default_data


    def is_divider(self, item):
        return set(item.strip()) == {"─"}

    def get_cpu_temperature(self):
        try:
            return temp.replace("temp=", "").replace("'C\n", "")
        except:
            return "N/A"

    def get_terminal_size(self):
        return f"{os.get_terminal_size().columns}x{os.get_terminal_size().lines}"

    def get_datetime(self):
        now = datetime.now(pytz.UTC)
        return now.strftime("%Y-%m-%d %H:%M:%S GMT")

    def get_latest_log(self):
        try:
            with open("notice.log", "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
                if lines:
                    return lines[-1]
                else:
                    return "No logs available"
        except Exception as e:
            return f"Error reading log: {e}"

    def update_utils_data(self):
        while True:
            try:
                with open("utils.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.utils_data = data
            except Exception:
                pass
            time.sleep(1)

    def get_status_text(self):
        try:
            cpu = f"{float(self.utils_data.get('cpu_usage', 0)):.1f}%"
        except Exception:
            cpu = "-"
        try:
            mem = f"{float(self.utils_data.get('memory_usage', 0)):.1f}%"
        except Exception:
            mem = "-"
        try:
            disk = f"{float(self.utils_data.get('disk_usage', 0)):.1f}%"
        except Exception:
            disk = "-"
        try:
            temp = f"{float(self.utils_data.get('temperature', 0)):.1f}°C"
        except Exception:
            temp = "-"
        return f"CPU: {cpu}\nMem: {mem}\nDisk: {disk}\nTemp: {temp}"

    def create_header(self):
        size_frame = Frame(
            Window(FormattedTextControl(lambda: f"{os.get_terminal_size().columns}x{os.get_terminal_size().lines}"),
                   align=WindowAlign.CENTER),
            width=12,
            height=3,
            title='Size'
        )
        datetime_frame = Frame(
            Window(FormattedTextControl(lambda: f"[OBC-GUI] DateTime: {self.utils_data.get('timestamp', 'unknown')}"), align=WindowAlign.CENTER),
            #lambda đối số: hàm thực hiện, nó là 1 hàm ẩn danh cũng là 1 hàm callback, ở lệnh trên thì nó chỉ có hàm k có đối số, và hàm lambda không thực hiện ngay mà sẽ được thực hiện khi có sự thay đổi giao diện, do GUI điều khiển, 
            #nên mỗi lần GUI thay đổi nó sẽ tự cập nhật, nếu không có lambda thì nó sẽ thực hiện hàm self.utils_data.get() ngay và không updateupdate
            width=None,
            height=3,
            title='Datetime'
        )
        status_frame = Frame(
            Window(FormattedTextControl("Active"), align=WindowAlign.CENTER),
            width=14, 
            height=3
        )

        return VSplit([size_frame, datetime_frame, status_frame])


    def setup_keybindings(self):
        #viết một hàm với sự kiện là nó sẽ thực hiện nếu ta bấm phím mũi tên lênlên
        @self.kb.add('up')
        def _(event):
            if self.mode == 'menu':
                selectable_count = sum(1 for item in self.menu_items if not self.is_divider(item))
                self.selected_item = max(0, self.selected_item - 1)
                self.lasted_selected_item = self.selected_item
                selectable_items = self.get_selectable_items()
                self.info_frame.title = selectable_items[self.selected_item]
                
            elif self.mode == 'info':
                selectable_items = self.get_selectable_items()
                if selectable_items[self.selected_item] == "SControl":
                    if self.selected_info > 0:
                        self.selected_info -= 1
                        current_field = self.settings_data["SControl"][self.selected_info]
                        if current_field["key"] != "Port":
                            self.port_buffer = None
            self.container = self.get_container()
            self.layout.container = self.container
            event.app.invalidate()

        @self.kb.add('down')
        def _(event):
            if self.mode == 'menu':
                selectable_count = sum(1 for item in self.menu_items if not self.is_divider(item))
                self.selected_item = min(selectable_count - 1, self.selected_item + 1)
                self.lasted_selected_item = self.selected_item
                selectable_items = self.get_selectable_items()
                self.info_frame.title = selectable_items[self.selected_item]
            elif self.mode == 'info':
                selectable_items = self.get_selectable_items()
                if selectable_items[self.selected_item] == "SControl":
                    max_info = len(self.settings_data["SControl"])  # "Apply" index = len(data)
                    self.selected_info = min(max_info, self.selected_info + 1)
                    if self.selected_info < len(self.settings_data["SControl"]):
                        current_field = self.settings_data["SControl"][self.selected_info]
                        if current_field["key"] != "Port":
                            self.port_buffer = None
            self.container = self.get_container()
            self.layout.container = self.container
            event.app.invalidate()

        @self.kb.add('enter')
        def _(event):
            if event.app.layout.has_focus(self.log_command_input):
                buf = self.log_command_input.buffer
                if buf.validate():  # Kiểm tra dữ liệu hợp lệ trước khi gửi
                    buf.accept_handler(buf)  # Gọi hàm xử lý khi nhấn Enter
            if self.mode == 'menu':
                selectable_items = self.get_selectable_items()
                if selectable_items[self.selected_item] == "Quit":
                    event.app.exit()
                else:
                    self.mode = 'info'
                    self.selected_info = 0
                    if selectable_items[self.selected_item] == "SControl":
                        current_field = self.settings_data["SControl"][self.selected_info]
                        if current_field["key"] == "Port":
                            self.port_buffer = current_field["value"]
                    elif selectable_items[self.selected_item] == "Logs":  # Focus vào TextArea
                        if hasattr(self, 'log_command_input'):
                            event.app.layout.focus(self.log_command_input)
                    else:
                        event.app.layout.focus(self.info_window)
                    self.lasted_selected_item = self.selected_item
            elif self.mode == 'info':
                selectable_items = self.get_selectable_items()
                selected_key = selectable_items[self.selected_item]
                if selected_key == "SControl":
                    data = self.settings_data["SControl"]
                    if self.selected_info < len(data):
                        current_field = data[self.selected_info]
                        if current_field["key"] != "Port":
                            current_field["value"] = "Disabled" if current_field["value"] == "Enabled" else "Enabled"
                    else:
                        filename = "SControl.json"
                        try:
                            with open(filename, "w", encoding="utf-8") as f:
                                json.dump(data, f, indent=4, ensure_ascii=False)
                        except Exception as e:
                            pass
                        self.mode = 'menu'
                        event.app.layout.focus(self.menu_window)
            self.container = self.get_container()
            self.layout.container = self.container            
            event.app.invalidate()

        @self.kb.add('escape')
        def _(event):
            if self.mode == 'info':
                self.mode = 'menu'
                self.selected_info = 0
                self.port_buffer = None
                event.app.layout.focus(self.menu_window)
                self.lasted_selected_item = self.selected_item
            self.container = self.get_container()
            self.layout.container = self.container
            event.app.invalidate()

        @self.kb.add('c-c')
        def _(event):
            event.app.exit()

        for digit in "0123456789": #tạo biến digit duyệt qua từng số từ 0 đến 9 để đăng kí cho hàm _()
            @self.kb.add(digit)    #bọc cái hàm ở dưới vào trong hàm kb với đối số là digit
            def _(event, digit=digit): #thì event ở đây sẽ là mỗi khi ta nhập 1 số từ bàn phím
                if self.mode == 'info':
                    selectable_items = self.get_selectable_items()  #tạo 1 bảng selectable_items với các phần tử không có dấu "-"
                    if selectable_items[self.selected_item] == "SControl":
                        current_field = self.settings_data["SControl"][self.selected_info] #current_field sẽ lưu 1 thành phần dict của Scontrol
                        if current_field["key"] == "Port":
                            if self.port_buffer is None or self.port_buffer == "0":
                                self.port_buffer = digit
                            else:
                                self.port_buffer += digit
                            current_field["value"] = self.port_buffer
                            self.lasted_selected_item = self.selected_item
                            event.app.invalidate()

       
        

        @self.kb.add('backspace')
        def _(event):
            #Kiểm tra xem test area có được focus không, ý là để nó biết backspace đang xử lí cho trường hợp nào á, nếu nó đang được focus thì 
            if event.app.layout.has_focus(self.log_command_input):
                buf = self.log_command_input.buffer
                if buf.cursor_position > 0:
                    buf.delete_before_cursor(count=1)
            if self.mode == 'info':
                selectable_items = self.get_selectable_items()
                if selectable_items[self.selected_item] == "SControl":
                    current_field = self.settings_data["SControl"][self.selected_info]
                    if current_field["key"] == "Port":
                        if self.port_buffer is not None and len(self.port_buffer) > 0:
                            self.port_buffer = self.port_buffer[:-1]
                            current_field["value"] = self.port_buffer if self.port_buffer else "0"
                            self.lasted_selected_item = self.selected_item
                            event.app.invalidate()
                
                
                    
        # @self.kb.add('c-r')
        # def _(event):
        #     self.container = self.get_container()
        #     self.layout.container = self.container
        #     event.app.invalidate()


    def create_menu_content(self):  #Tạo 1 list lồng tuple têntên content để lưu trang thái của cả cái menu, là kiểu đang chọn cái nào thì nó đổi màu cái đó
        content = []          #Nó sẽ lưu thành 1 list nhiều tuple, mỗi tuple là 1 cặp gồm (trạng thái màu, nội dungdung)
        selectable_index = 0  #Biến để chỉ vị trí cần tô sáng

        for item in self.menu_items:
            if self.is_divider(item): 
                content.append(('', item + "\n"))  #nếu nó duyệt thấy là dấu - thì nó sẽ kh có trạng thái màu và nội dung là cái item đó với việc xuống dòng
            else: #nếu nó không phải là các dấu - thì nó là các đề mục của mục menu 
                style = 'class:menu.selected' if selectable_index == self.selected_item else 'bold' #nếu cái index của hàm này bằng với cái self.selected_item, nghĩa là ta đang chọn mục đó thì nó sẽ lưu tuple(với style là class..., nội dung), còn không thì nó chỉ có style là bold
                content.append((style, f"{item}\n"))
                selectable_index += 1
        return content

        
    def get_selectable_items(self):
        return [item.strip() for item in self.menu_items if not self.is_divider(item)]

    
    #Trong hàm dưới đây đã có set title, là nó đặt cái nội dung tiltle ra đè lên cái viền
    def create_info_content(self):
        selectable_items = self.get_selectable_items()       #trả về 1 list không có các dấu "-"
        selected_key = selectable_items[self.selected_item]  #lấy 1 phần tử của list tùy theo cái con trỏ đang nằm ở đâuđâu
        if selected_key == "Quit": #căn chỉnh bảng inffor cho Quit
            logo = self.settings_data.get("Quit", "\n  No information available") #phương thức get(key,default_value), là lấy giá trị với key tương ứng, nếu k có sẽ trả về default_value(do ta định nghĩa) và không gây crack chương trình
            term_size = os.get_terminal_size()
            term_width = term_size.columns-28
            fixed_info_height = 0  # chiều cao cố định của vùng info
            logo_lines = logo.splitlines() #hàm tách chuỗi lưu trong logo thành danh sách dựa trên kí tự \n trong chuỗi logo
            num_logo_lines = len(logo_lines)
            pad_top = 0   
            centered_lines = [] 
            for _ in range(pad_top):  #tạo dòng trống phía trên, này bằng 0 thì không có dòng trống nào thì khi in cái logo_lines thì nó không có khoảng trống phía trên
                centered_lines.append(('', '\n')) #pad_top = 0 nên là không có dòng nào
            for line in logo_lines: #căn giữa từng dòng trong logo_lineslines
                centered_lines.append(('class:info', line.center(term_width))) #với mỗi dòng trong logo_lines, dùng line.center(term_width) để căn giữa dòng đó theo chiều rộng term_width.
            return centered_lines  #các phần tử được căn giữa sẽ lưu vào centered_lines
        
        elif selected_key == "SControl": #dùng để hiển thị sáng lên cái dòng đang được chọn trong bản infor
            content = [] #tạo 1 tuple lưu text và trạng thái dòng text tương ứng
            content.append(('class:info.title', f"\n  {selected_key} Settings:\n\n"))#dùng để thêm 1 thành phần tuple là  1 text với trạng thái dòng text ở đây dòng đó là Scontrol và nó cũng được đặt vị trí tiêu đề, chèn lên cái frame
            data = self.settings_data["SControl"]
            for i, item in enumerate(data):  #trả về index và 1 phần tử dict của data
                if self.selected_info == i and self.mode == 'info':
                    key_style = 'class:info.selected'    #nếu con trỏ đang nằm tại vị trí đó, con trỏ thì nó lưu trong self.selected_info thì nó sẽ lưu cái style nổi bật ở đó
                    value_style = 'class:info.selected'  
                else:
                    key_style = 'class:key'
                    value_style = 'class:value'
                content.append((key_style, f"  {item['key']}: ")) #dòng trên và dòng dưới là nó lưu 1 cặp tuple, cặp thứ nhất là key và trạng thái, cặp thuứ 2 là value và trạng thái, mà ở đây cái key là cái giá trị của cái key thứ nhất và value là giá trị của cái key thứ 2
                content.append((value_style, f"{item['value']}\n"))
            if self.selected_info == len(data) and self.mode == 'info':
                apply_style = 'class:info.selected'
            else:
                apply_style = 'class:info'
            term_size = os.get_terminal_size()
            term_width = term_size.columns-28
            apply_text = "[ Apply ]".center(term_width)
            content.append((apply_style, apply_text+"\n"))
            return content #nó sẽ trả về 1 list chứa các tuple, mỗi tuple sẽ là style của text với text là key hoặc value
            
            
            #đây là chỗ ta sẽ tạo thêm 1 trường hơp nếu nó là logs để cho nó hiển thị cái khuing nhập luioonuioon
            
        elif selected_key == "Tracking":
            content = self.formatted 
            return content
        

        elif selected_key in self.settings_data:
            content = []
            content.append(('class:info.title', f"\n  {selected_key} Settings:\n\n"))
            data = self.settings_data[selected_key]
            for item in data:
                content.append(('class:key', f"  {item['key']}: "))
                content.append(('class:value', f"{item['value']}\n"))
            return content

        else:
            return [('class:info', "\n  No information available")]
        
    
    #Tính giá trị trung bình, xét điều kiện lớn hơn 2 là do bỏ 2 giá trị đầu, kiểm tra những số khác 0 và chỉ lấy trung bình những số đó
    def avarage (self):
        a = 0
        sum = 0
        for i,value in enumerate(self.output_log_line):
            if (i > 1) and (value != 0):
                sum += value
                a+=1
            continue
        return sum/a 
    

    #Tiền xủ lý khi đọc từ file.log về
    def process_data(self,log_line):                
        patern = r"C(\d+)-(\d+)"\
                r".*?\[T: 0\]-\[ADC: (\d+)\]"\
                r"(?:.*?\[T: 1\]-\[ADC: (\d+)\])?"\
                r"(?:.*?\[T: 2\]-\[ADC: (\d+)\])?"\
                r"(?:.*?\[T: 3\]-\[ADC: (\d+)\])?"
        match = re.search(patern, log_line)
#patern ở đây là 1 regrex dùng để đối chiếu với 1 hàng trong file log, do mỗi lần ta đọc về từ file.log là ta đọc 1 hàng
#thì ở đây nó trả về 6 cái (\d+) bao gồm hàng, côt, lần lấy 0,1,2,3
#match = re.search() sẽ lưu nó vào matchmatch

        if match:
            self.output_log_line = list(match.groups()) #match.groups() là lấy tất cả những gì có trong match, list() là lưu nó vào 1 biến mới dưới dạng list
            self.output_log_line = [0 if x is None else x for x in self.output_log_line]
            self.output_log_line = list(map(int,self.output_log_line))
            self.sensor_value[self.output_log_line[0]-1][self.output_log_line[1]-1] = self.avarage()
            #return self.sensor_value
            self.format_table(self.output_log_line[0],self.output_log_line[1])
        
        else:
            print("Không tìm thấy dữ liệu cảm biến!")

    def send_to_matrix(self):
        with open("test.log", "r", encoding="utf-8") as file:
            for log_line in file:
                if "ADC" in log_line: #kiểm tra trong dòng log đó có kí tự nào là ADC k, nếu có thì cho phép đọc dòng đó vì đó là dòng có giá trị cảm biến
                    self.process_data(log_line)
                    time.sleep(1)
                    #app.invalidate()

    def format_table(self,x,y):
        self.formatted = []
        table_str = tabulate(self.sensor_value,tablefmt="grid").split("\n")
        semaphore = 0
        row_indx, col_indx = 0,0
        for i,row in enumerate(table_str):
            if i % 2 == 0:
                for char in row:
                    self.formatted.append(("fg:white",char))
                self.formatted.append(("fg:white","\n"))
            if i % 2 != 0:
                col_indx = 0
                semaphore = 0
                for char in row:
                    if char.isdigit() or char == "." or " ":
                        if row_indx == (x-1) and col_indx == (y-1):
                            self.formatted.append(("bg:yellow",char))
                        else:
                            self.formatted.append(("fg:white",char))              
                    if char == "|":
                        #self.formatted.append(("fg:white",char))
                        semaphore +=1
                        if semaphore > 1:
                            col_indx +=1
                    # else:
                    #     self.formatted.append(("fg:white",char))
                self.formatted.append(("fg:white","\n"))
                row_indx +=1
        return self.formatted












    def handle_log_command(self, buffer):
        self.text_from_command = buffer.text.strip()
        # if command:
        #     try:
        #         # Ví dụ các lệnh xử lý
        #         if command.lower() == "clear errors":
        #             self.settings_data["Logs"][1]["value"] = "0"  # Reset Errors
        #         elif command.lower().startswith("set level "):
        #             level = command.split(" ", 2)[2].upper()
        #             if level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
        #                 self.settings_data["Logs"][0]["value"] = level
        #         elif command.lower() == "show latest":
        #             latest_log = self.get_latest_log()
        #             self.log_command_input.text = latest_log  # Hiển thị log mới nhất
        #         elif command.lower() == "view log":
        #             try:
        #                 with open("notice.log", "r", encoding="utf-8") as f:
        #                     self.log_command_input.text = f.read()[:100]  # Giới hạn 100 ký tự
        #             except Exception as e:
        #                 self.log_command_input.text = f"Error: {e}"

        #         # Lưu thay đổi vào file Logs.json
        #         with open("Logs.json", "w", encoding="utf-8") as f:
        #             json.dump(self.settings_data["Logs"], f, indent=4, ensure_ascii=False)

        #         # Nếu không phải lệnh "show latest", xóa input sau khi xử lý
        #         if not command.lower() == "show latest":
        #             self.log_command_input.text = ""
        #     except Exception as e:
        #         self.log_command_input.text = f"Error: {str(e)}"

        return True  # Giữ TextArea hoạt động

    
    def get_container(self):
        header = self.create_header()

        self.menu_window = Window(FormattedTextControl(self.create_menu_content), width=10)
        side_window = Window(FormattedTextControl("Additional"), width=12)

        

        
        # Tạo cửa sổ hiển thị thông tin Logs
        self.info_up_window = Window(FormattedTextControl(self.create_info_content), width=None, height=None)  # Giới hạn chiều cao
      
        if (self.selected_item == 4):
            #Tạo TextArea cho command input
            if not hasattr(self, 'log_command_input'):
                print("Creating log_command_input")  # Debug
                self.log_command_input = TextArea(
                    height=3,
                    prompt=">>> ",
                    multiline=False,
                    accept_handler=self.handle_log_command
                )
            self.cmd_frame = Frame(self.log_command_input, title="Command Line", width=None, height=3)
            text_input = Window(FormattedTextControl(lambda: f"BAN DA NHAP: {self.text_from_command}"),width=None,height=None)
                    # Kết hợp info và command input theo chiều dọc
            self.info_window = HSplit([
                self.info_up_window,
                text_input,
                self.cmd_frame
            ], width=None, height= None)  # Đảm bảo chiều rộng tự động
                    
            self.info_frame = Frame(self.info_window, title="Logs",width=None, height=None)
        
        else:
            self.info_window = Window(FormattedTextControl(self.create_info_content), width=None)
            self.info_frame = Frame(self.info_window, title = lambda: f"{self.menu_list[self.selected_item]}")
        




        main_content = VSplit([
            Frame(self.menu_window, title="Menu"),
            self.info_frame,
            Frame(side_window, title="Data")
        ])

        log_window = Window(FormattedTextControl(lambda: f">>>ITEM: {self.selected_item}"), height=1, style='class:log')

        status_bar = VSplit([
            Window(FormattedTextControl("↑↓: Navigate | Enter: Select | Esc: Back | Ctrl+C: Exit"), style='class:status'),
            Window(FormattedTextControl("--------.com"), align=WindowAlign.RIGHT, style='#1313c2')
        ], height=1)

        return HSplit([header, main_content, Frame(log_window), status_bar])
    

    #Ở đây vấn đề là do ta gọi cái self.get_container để truyền chỉ 1 lần đầu tiên ta run() nên nó không thể cặp nhật trạng thái bảng dù cho biến selected_item có thay đổi
    #biến đó nó thay đổi thì khi ta dùng event.app.invalidate() thì nó chỉ vẽ lại nội dung thôi còn cái mà layout cái bảng từ self.get_container vẫn cố định do nó đã truyền cố định lúc đầu
    #nên ở đây ta phải chèn vào cái event mà cho nó liên tục cập nhật lại cái self.get_container hay có thể hiểu là gọi cái đó ra nhiều lần thì nó mới check điều kiện tại thời điểm nó gọi xem như nào ròi nó mới thực hiện được
    # 1 sai lầm NGHIÊM TRỌNG là tôi kiểm tra điều kiện trong cái hàm nhưng tôi lại gọi hàm đó có 1 lần:)))  

    
    def run(self):
        self.layout = Layout(container=self.get_container())
        app = Application(
            layout=self.layout,
            key_bindings=self.kb,
            style=self.style,
            full_screen=True,
            mouse_support=True,
            refresh_interval=1 
        )
        
        app.run()
    
def main():
    gui = RaspiGUI()
    gui.run()

if __name__ == "__main__":
    main()



'''
tạo 1 bảng command line trong thanh logs

Làm sao để đặt 1 cửa sổ vào trong 1 cửa sổ đã có sẵn
cái cửa sổ log đó chỉ xuất hiện khi infor là của menu logs
Thì do nó lưu mọi thứ vào 1 cái infor conten thì cái tạo cái cửa sổ infor nó chỉ có nghĩa vụ hiện ra cái cửa sổ hiển thị những cái đã chưas thôi
giờ làm sao cho trong 1 cái cửa sổ mà nó hiện thêm khung frame để cho phép nhập chứ k chỉ hiển thị
thì ý tưởng code ở trên nó chỉ có thể nhập bằng việc đăng kí các event thôi, event xảy ra thì nó sẽ lại lưu giá trị mới vào 1 file và nó cứ thế hiển thị lại ra màn hình cái file mới đó
vậy ý tưởng là cũng lưu cái cmd vào 1 file mỗi khi ta nhập, xong nó lại đối chiếú cái đó với những nội dung từ yêu cầu tương ứng mà có sẵn khi ta lưu ở 1 file và lấy cái nội dung hiển thị đó ra

- Viết 1 hàm riêng để hiển thị infor của cái logs, thì khi ta gọi để in ra cửa sổ ta sẽ dựa vào cái self.selected_item để biết nên hiển thị cửa sổ nào
- 

Ý tưởng mới:
Cái cửa sổ để hiển thị ra cái infor create_info_content(self) nó có chia các trườnh hợp là gồm Quit và Scontrol rồ thì giơd cho nó thêm một trườmh hợp nó là cái Logs thì mình tạo hẳn cái 
window mới trong cái đó luôn
Hmm nhưng mà cái đó nó trả về list tuple.. nên không thể chèn cái frame vào đó được


Ý tưởng mới mới
Khi layout ở cái hàm get_container() thì so sánh xem nó có logs không thì nếu nó là cửa số logs thì chèn nó thêm cái frame
-------------------
DONE
'''



'''
TASK MỚI:
Hiển thi 1 ma trận dữ liệu 6x6 gửi ra từ cảm biến trên cửa sổ tracking
1/Tìm hiểu cái dạng file ghi cảm biến và đọc về
done!
2/Tìm cách đọc đúng cái giá trị trên cái dòng đó
done!
- Trong file read_log.py
lỗi phát sinh:
Khi ta đọc về nhưng nếu giá trị đó cảm biến trả về có 2 lần thôi mà ta so sánh điều kiện có T2 thì nó sẽ lỗi
3/Tìm cách lưu nó vào đâu đó để hiển thị:
Done 
4/Làm sao để hiển thị mỗi giá trị sáng lên khi mỗi lần cập nhật:
Viết 1 hàm để truyền vào vị trí nào thì nó thay đổi màu khác, còn các vị trí còn lại thì màu trắng bình thường
- Mỗi lần cập nhật về thì nó có vị trí rồi,
- Giờ ở đây là cần 
'''


'''
Ý tưởng là ta sẽ đưa nó về chuỗi
'''


        
        