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

class RaspiGUI:
    def __init__(self):
        self.port_buffer = None
        self.kb = KeyBindings()
        self.mode = 'menu'
        self.selected_item = 0
        self.selected_info = 0
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

        self.utils_data = {
            "timestamp": "unknown",
            "cpu_usage": 0,
            "memory_usage": 0,
            "disk_usage": 0,
            "temperature": 0
        }
        threading.Thread(target=self.update_utils_data, daemon=True).start()
        
        self.setup_keybindings()

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
        @self.kb.add('up')
        def _(event):
            if self.mode == 'menu':
                selectable_count = sum(1 for item in self.menu_items if not self.is_divider(item))
                self.selected_item = max(0, self.selected_item - 1)
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
            event.app.invalidate()

        @self.kb.add('down')
        def _(event):
            if self.mode == 'menu':
                selectable_count = sum(1 for item in self.menu_items if not self.is_divider(item))
                self.selected_item = min(selectable_count - 1, self.selected_item + 1)
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
            event.app.invalidate()

        @self.kb.add('enter')
        def _(event):
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
                    event.app.layout.focus(self.info_window)
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
            event.app.invalidate()

        @self.kb.add('escape')
        def _(event):
            if self.mode == 'info':
                self.mode = 'menu'
                self.selected_info = 0
                self.port_buffer = None
                event.app.layout.focus(self.menu_window)
            event.app.invalidate()

        @self.kb.add('c-c')
        def _(event):
            event.app.exit()
        for digit in "0123456789":
            @self.kb.add(digit)
            def _(event, digit=digit):
                if self.mode == 'info':
                    selectable_items = self.get_selectable_items()
                    if selectable_items[self.selected_item] == "SControl":
                        current_field = self.settings_data["SControl"][self.selected_info]
                        if current_field["key"] == "Port":
                            if self.port_buffer is None or self.port_buffer == "0":
                                self.port_buffer = digit
                            else:
                                self.port_buffer += digit
                            current_field["value"] = self.port_buffer
                            event.app.invalidate()

        @self.kb.add('backspace')
        def _(event):
            if self.mode == 'info':
                selectable_items = self.get_selectable_items()
                if selectable_items[self.selected_item] == "SControl":
                    current_field = self.settings_data["SControl"][self.selected_info]
                    if current_field["key"] == "Port":
                        if self.port_buffer is not None and len(self.port_buffer) > 0:
                            self.port_buffer = self.port_buffer[:-1]
                            current_field["value"] = self.port_buffer if self.port_buffer else "0"
                            event.app.invalidate()


    def create_menu_content(self):
        content = []
        selectable_index = 0 

        for item in self.menu_items:
            if self.is_divider(item):
                content.append(('', item + "\n"))
            else:
                style = 'class:menu.selected' if selectable_index == self.selected_item else 'bold'
                content.append((style, f"{item}\n"))
                selectable_index += 1
        return content

        
    def get_selectable_items(self):
        return [item.strip() for item in self.menu_items if not self.is_divider(item)]


    def create_info_content(self):
        selectable_items = self.get_selectable_items()
        selected_key = selectable_items[self.selected_item]
        if selected_key == "Quit":
            logo = self.settings_data.get("Quit", "\n  No information available")
            term_size = os.get_terminal_size()
            term_width = term_size.columns-28
            fixed_info_height = 0  # chiều cao cố định của vùng info
            logo_lines = logo.splitlines()
            num_logo_lines = len(logo_lines)
            pad_top = 0
            centered_lines = []
            for _ in range(pad_top):
                centered_lines.append(('', '\n'))
            for line in logo_lines:
                centered_lines.append(('class:info', line.center(term_width)))
                centered_lines.append(('', '\n'))
            return centered_lines
        elif selected_key == "SControl":
            content = []
            content.append(('class:info.title', f"\n  {selected_key} Settings:\n\n"))
            data = self.settings_data["SControl"]
            for i, item in enumerate(data):
                if self.selected_info == i and self.mode == 'info':
                    key_style = 'class:info.selected'
                    value_style = 'class:info.selected'
                else:
                    key_style = 'class:key'
                    value_style = 'class:value'
                content.append((key_style, f"  {item['key']}: "))
                content.append((value_style, f"{item['value']}\n"))
            if self.selected_info == len(data) and self.mode == 'info':
                apply_style = 'class:info.selected'
            else:
                apply_style = 'class:info'
            term_size = os.get_terminal_size()
            term_width = term_size.columns-28
            apply_text = "[ Apply ]".center(term_width)
            content.append((apply_style, apply_text+"\n"))
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

    def get_container(self):
            header = self.create_header()

            self.menu_window = Window(FormattedTextControl(self.create_menu_content), width=10)
            self.info_window = Window(FormattedTextControl(self.create_info_content), width=None)
            side_window = Window(FormattedTextControl("Additional"), width=12)

            self.info_frame = Frame(self.info_window, title="Information")

            main_content = VSplit([
                Frame(self.menu_window, title="Menu"),
                self.info_frame,
                Frame(side_window, title="Data")
            ])

            log_window = Window(FormattedTextControl(lambda: f">>> {self.get_latest_log()}"), height=1, style='class:log')

            status_bar = VSplit([
        Window(FormattedTextControl("↑↓: Navigate | Enter: Select | Esc: Back | Ctrl+C: Exit"), style='class:status'),
        Window(FormattedTextControl("--------.com"), align=WindowAlign.RIGHT, style='#1313c2')
    ], height=1)

            return HSplit([header, main_content, Frame(log_window), status_bar])

    def run(self):
        layout = Layout(container=self.get_container())
        app = Application(
            layout=layout,
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