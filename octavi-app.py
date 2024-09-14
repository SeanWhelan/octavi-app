import sys
import os
import subprocess
import glob
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTextEdit, QSplitter,
                             QListWidget, QInputDialog, QLineEdit, QLabel)
from PyQt6.QtGui import QIcon, QPixmap, QPainter
from PyQt6.QtCore import Qt, QSize, QTimer, QRect

class UdevRulesApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.list_octavi_rules()  # Call this method when the app starts

    def initUI(self):
        self.setWindowTitle('Udev Rules Manager')
        self.setGeometry(100, 100, 1200, 700)  # Increased width to accommodate the larger right panel

        # Create main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Add image
        image_label = QLabel()
        pixmap = QPixmap("octavi_ifr1.jpg")
        scaled_pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        image_label.setPixmap(scaled_pixmap)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(image_label)

        # Create horizontal splitter for main content and instructions
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side (main content)
        left_widget = QWidget()
        left_layout = QVBoxLayout()

        # Create vertical splitter for top and bottom panels
        content_splitter = QSplitter(Qt.Orientation.Vertical)

        # Top panel
        top_panel = QWidget()
        top_layout = QVBoxLayout()

        # Button panel
        button_panel = QWidget()
        button_layout = QHBoxLayout()

        # Create buttons with icons and tooltips
        btn_list = self.create_button("folder", "List Octavi Rules", 
                                      tooltip="List all Octavi-related udev rules")
        btn_reload = self.create_button("view-refresh", "Reload Rules", True, 
                                        tooltip="Reload udev rules (requires sudo)")
        btn_trigger = self.create_button("system-run", "Trigger Rules", True, 
                                         tooltip="Trigger udev rules (requires sudo)")
        btn_hidraw = self.create_button("dialog-information", "Show Hidraw Permissions", 
                                        tooltip="Display permissions for hidraw devices")
        btn_dmesg = self.create_button("utilities-terminal", "Dmesg Hidraw", True, 
                                       tooltip="Show hidraw-related kernel messages (requires sudo)")
        btn_create_rule = self.create_button("document-new", "Create Udev Rule", True, 
                                             tooltip="Create a new udev rule for Octavi (requires sudo)",
                                             additional_icon="edit-write")
        btn_find_octavi = self.create_button("edit-find", "Find Octavi Device", True, 
                                             tooltip="Search for Octavi devices and set permissions (requires sudo)",
                                             additional_icon="system-search")

        btn_list.clicked.connect(self.list_octavi_rules)
        btn_reload.clicked.connect(self.reload_rules)
        btn_trigger.clicked.connect(self.trigger_rules)
        btn_hidraw.clicked.connect(self.show_hidraw_permissions)
        btn_dmesg.clicked.connect(self.dmesg_hidraw)
        btn_create_rule.clicked.connect(self.create_udev_rule)
        btn_find_octavi.clicked.connect(self.run_find_octavi_device)

        button_layout.addWidget(btn_list)
        button_layout.addWidget(btn_reload)
        button_layout.addWidget(btn_trigger)
        button_layout.addWidget(btn_hidraw)
        button_layout.addWidget(btn_dmesg)
        button_layout.addWidget(btn_create_rule)
        button_layout.addWidget(btn_find_octavi)
        button_panel.setLayout(button_layout)

        # File list
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.display_file_contents)

        top_layout.addWidget(button_panel)
        top_layout.addWidget(self.file_list)
        top_panel.setLayout(top_layout)

        # Bottom panel (output)
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)

        # Add panels to content splitter
        content_splitter.addWidget(top_panel)
        content_splitter.addWidget(self.output_text)

        left_layout.addWidget(content_splitter)
        left_widget.setLayout(left_layout)

        # Right side (instructions)
        self.instructions_text = QTextEdit()
        self.instructions_text.setReadOnly(True)
        self.set_instructions()

        # Add widgets to main splitter
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(self.instructions_text)
        main_splitter.setSizes([400, 800])  # Set initial sizes for left and right panels

        # Add main splitter to main layout
        main_layout.addWidget(main_splitter)

        # Exit button
        btn_exit = QPushButton(QIcon.fromTheme("application-exit"), "Exit")
        btn_exit.clicked.connect(self.close)
        main_layout.addWidget(btn_exit)

        # Set main widget and layout
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def create_button(self, icon_name, text, sudo=False, tooltip="", additional_icon=None):
        button = QPushButton(text)
        button.setIconSize(QSize(24, 24))  # Set a fixed icon size
        button.setStyleSheet("QPushButton { text-align: left; padding-left: 5px; }")
        
        main_icon = QIcon.fromTheme(icon_name)
        
        if sudo or additional_icon:
            combined_icon = QIcon()
            base_pixmap = main_icon.pixmap(24, 24)
            combined_pixmap = QPixmap(base_pixmap.size())
            combined_pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(combined_pixmap)
            painter.drawPixmap(0, 0, base_pixmap)
            
            if sudo:
                sudo_icon = QIcon.fromTheme("dialog-password")
                painter.drawPixmap(QRect(12, 12, 12, 12), sudo_icon.pixmap(12, 12))
            
            if additional_icon:
                add_icon = QIcon.fromTheme(additional_icon)
                painter.drawPixmap(QRect(0, 12, 12, 12), add_icon.pixmap(12, 12))
            
            painter.end()
            combined_icon = QIcon(combined_pixmap)
            button.setIcon(combined_icon)
        else:
            button.setIcon(main_icon)
        
        if tooltip:
            button.setToolTip(tooltip)
        
        return button

    def list_octavi_rules(self):
        self.file_list.clear()
        rules_dir = '/etc/udev/rules.d/'
        try:
            for filename in os.listdir(rules_dir):
                if 'octavi' in filename.lower():
                    self.file_list.addItem(filename)
            if self.file_list.count() == 0:
                self.output_text.setPlainText("No Octavi rules found.")
            else:
                self.output_text.setPlainText(f"Found {self.file_list.count()} Octavi rule(s).")
        except Exception as e:
            self.output_text.setPlainText(f"Error listing files: {str(e)}")

    def display_file_contents(self, item):
        filename = item.text()
        file_path = os.path.join('/etc/udev/rules.d/', filename)
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            self.output_text.setPlainText(content)
        except Exception as e:
            self.output_text.setPlainText(f"Error reading file: {str(e)}")

    def reload_rules(self):
        self.run_sudo_command("udevadm control --reload-rules")

    def trigger_rules(self):
        self.run_sudo_command("udevadm trigger")

    def run_sudo_command(self, command, password=None, callback=None):
        if password is None:
            password, ok = QInputDialog.getText(self, "Sudo Password", "Enter sudo password:", QLineEdit.EchoMode.Password)
            if not ok:
                self.output_text.setPlainText("Operation cancelled.")
                return

        full_command = f"echo {password} | sudo -S {command}"
        try:
            result = subprocess.run(full_command, shell=True, check=True, capture_output=True, text=True)
            output = result.stdout if result.stdout else "Command executed successfully."
            if callback:
                callback(output)
            else:
                self.output_text.setPlainText(output)
        except subprocess.CalledProcessError as e:
            output = f"Error executing command: {e.stderr}"
            self.output_text.setPlainText(output)

    def show_hidraw_permissions(self):
        try:
            hidraw_devices = glob.glob('/dev/hidraw*')
            if not hidraw_devices:
                self.output_text.setPlainText("No hidraw devices found.")
                return

            output = "Hidraw device permissions:\n\n"
            for device in hidraw_devices:
                ls_output = subprocess.check_output(['ls', '-l', device], universal_newlines=True).strip()
                output += f"{ls_output}\n"

            self.output_text.setPlainText(output)
        except Exception as e:
            self.output_text.setPlainText(f"Error retrieving hidraw permissions: {str(e)}")

    def dmesg_hidraw(self):
        def highlight_octavi_ifr1(output):
            lines = output.split('\n')
            highlighted_lines = []
            for line in lines:
                if 'octavi ifr1' in line.lower():
                    highlighted_lines.append(f"<b>{line}</b>")
                else:
                    highlighted_lines.append(line)
            return '<br>'.join(highlighted_lines)

        def process_output(output):
            highlighted_output = highlight_octavi_ifr1(output)
            self.output_text.setHtml(highlighted_output)

        self.run_sudo_command("dmesg | grep -i 'hidraw\\|octavi'", callback=process_output)

    def create_udev_rule(self):
        command = 'echo "SUBSYSTEM==\\"usb\\", ATTR{idVendor}==\\"04d8\\", ATTR{idProduct}==\\"e6d6\\", MODE=\\"0666\\"" > /etc/udev/rules.d/99-octavi.rules'
        self.run_sudo_command(command)
        self.output_text.setPlainText("Udev rule created. Please reload rules and trigger udev for changes to take effect.")

    def find_octavi_device(self, password):
        VENDOR_ID = "04D8"
        PRODUCT_ID = "E6D6"
        
        found_devices = []
        
        self.output_text.setPlainText("Searching for Octavi IFR1 devices...")
        QApplication.processEvents()
        
        hidraw_devices = glob.glob('/dev/hidraw*')
        
        for hidraw in hidraw_devices:
            try:
                device_info = subprocess.check_output(['sudo', '-S', 'udevadm', 'info', '--query=all', '--name=' + hidraw], 
                                                  input=password if isinstance(password, bytes) else password.encode(),
                                                  stderr=subprocess.PIPE)
                
                # Decode the bytes to a string
                device_info_str = device_info.decode('utf-8')
                
                devpath_match = re.search(r'DEVPATH=.*0003:([0-9A-Fa-f]{4}):([0-9A-Fa-f]{4})', device_info_str)
                
                if devpath_match:
                    current_vendor_id, current_product_id = devpath_match.groups()
                    
                    if current_vendor_id.upper() == VENDOR_ID and current_product_id.upper() == PRODUCT_ID:
                        found_devices.append(hidraw)
            except subprocess.CalledProcessError:
                continue

        if found_devices:
            result = "Found Octavi IFR1 device(s):\n"
            for device in found_devices:
                result += f"{device}\n"
                try:
                    subprocess.run(['sudo', '-S', 'chmod', '0666', device], input=password.encode(), check=True)
                    result += f"Applied chmod 0666 to {device}\n"
                except subprocess.CalledProcessError:
                    result += f"Failed to apply chmod 0666 to {device}\n"
        else:
            result = "No Octavi IFR1 devices found."

        self.output_text.setPlainText(result)
        QApplication.processEvents()

    def run_find_octavi_device(self):
        password, ok = QInputDialog.getText(self, "Sudo Password", "Enter sudo password:", QLineEdit.EchoMode.Password)
        if ok:
            self.output_text.clear()
            self.output_text.setPlainText("Preparing to search for Octavi IFR1 devices...")
            QTimer.singleShot(100, lambda: self.find_octavi_device(password))
        else:
            self.output_text.setPlainText("Operation cancelled.")

    def set_instructions(self):
        instructions = """
        Instructions:

        1. List Octavi Rules: Display all Octavi-related udev rules.
        2. Reload Rules: Reload udev rules (requires sudo).
        3. Trigger Rules: Trigger udev rules (requires sudo).
        4. Show Hidraw Permissions: Display permissions for hidraw devices.
        5. Dmesg Hidraw: Show hidraw-related kernel messages (requires sudo).
        6. Create Udev Rule: Create a new udev rule for Octavi (requires sudo).
        7. Find Octavi Device: Search for Octavi devices and set permissions (requires sudo).

        Note: Actions marked with (requires sudo) will prompt for your password.
        """
        self.instructions_text.setPlainText(instructions)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = UdevRulesApp()
    ex.show()
    sys.exit(app.exec())