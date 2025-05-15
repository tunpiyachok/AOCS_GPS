from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import os
from functools import partial
import zipfile
import subprocess
import datetime

class CubeSatGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KU CubeSat")
        self.setGeometry(0, 0, 1440, 1024)
        self.setStyleSheet("background-color: #F1F1F1; color: black;")
        
        self.top_bar_main = self.createTopBarMain()  # 🔹 Top Bar สำหรับหน้าหลัก
        self.top_bar_log = self.createTopBarLog()  # 🔹 Top Bar สำหรับ Log File
        self.top_bar_pic = self.createTopBarPic() # 🔹 Top Bar สำหรับ Log File

        self.createBottomBar()

        self.createMissionPlanBox()
        self.createTelecommandBox()
        self.createTelemetryBox()
        self.createPayloadTM()
        self.createfswTM()
        self.createGPSTM()
        self.cleared_files = set()
        self.cleared_files_pic = set()
        
        self.stack = QStackedWidget(self)

        self.mainWidget = QWidget()
        self.initMainUI()  # เรียก UI ของหน้าหลัก

        self.logFileWidget = QWidget()
        self.initLogFileUI()  # เรียก UI ของหน้า Log File

        self.picWidget = QWidget()
        self.initPictureListUI()  # เรียก UI ของหน้า Log File

        self.stack.addWidget(self.mainWidget)
        self.stack.addWidget(self.logFileWidget)
        self.stack.addWidget(self.picWidget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.stack)
        main_layout.addWidget(self.bottom_bar)
        main_layout.setStretch(0, 1)

        self.setLayout(main_layout)

        self.stack.setCurrentWidget(self.mainWidget)

    def initMainUI(self):
        """UI ของหน้าหลัก """
        layout = QVBoxLayout(self.mainWidget)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.top_bar_main)

        body_layout = QHBoxLayout()

        sidebar = QVBoxLayout()
        sidebar.addSpacing(20)
        sidebar.addLayout(self.missionPlanLayout)
        sidebar.addSpacing(10)
        sidebar.addLayout(self.telecommandLayout)
        sidebar.addSpacing(10)
        sidebar.addLayout(self.telemetryLayout)
        sidebar.addSpacing(10)
        sidebar.addLayout(self.payloadLayout)
        sidebar.addSpacing(10)
        sidebar.addLayout(self.fswLayout)
        sidebar.addSpacing(10)
        sidebar.addLayout(self.GPSLayout)
        sidebar.addStretch(1)

        content_layout = QVBoxLayout()
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        image_layout = QHBoxLayout()

        spacer_left = QSpacerItem(50, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        image_layout.addItem(spacer_left)

        self.image_frame = QLabel("โปรดรอรูปภาพ...", self)
        self.image_frame.setFixedSize(550, 380)
        self.image_frame.setStyleSheet("""
            border: 2px solid black;
            background-color: white;
            font-size: 18px;
            color: gray;
        """)
        self.image_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_layout.addWidget(self.image_frame)

        spacer_right = QSpacerItem(50, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        image_layout.addItem(spacer_right)

        self.image_folder = r"C:\Users\tuaok\Pictures\CS-Project\picture"

        self.timer = QTimer()
        self.timer.timeout.connect(self.uploadLatestImage)
        self.timer.start(0) 

        self.uploadLatestImage()

        content_layout.addLayout(image_layout)

        self.log_file_button = QPushButton("Log File", self)
        self.log_file_button.setFixedSize(150, 50)
        self.log_file_button.setStyleSheet("""
            background-color: #007BFF;
            color: white;
            font-size: 18px;
            border-radius: 10px;
            padding: 5px;
        """)
        self.log_file_button.clicked.connect(self.openLogFilePage)


        self.picture_list_button = QPushButton("Picture List", self)
        self.picture_list_button.setFixedSize(150, 50)
        self.picture_list_button.setStyleSheet("""
            background-color: #28A745;
            color: white;
            font-size: 18px;
            border-radius: 10px;
            padding: 5px;
        """)
        self.picture_list_button.clicked.connect(self.openPictureList)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.log_file_button)
        button_layout.addWidget(self.picture_list_button)


        content_layout.addLayout(button_layout)

        body_layout.addLayout(sidebar, 1)
        body_layout.addLayout(content_layout, 3)

        layout.addLayout(body_layout)
        layout.addWidget(self.bottom_bar)

    def createTopBarMain(self):
        """สร้าง Top Bar สำหรับหน้าหลัก"""
        top_bar = QFrame()
        top_bar.setFixedHeight(100)
        top_bar.setStyleSheet("""
            background-color: #1D3557;
            padding: 0px;
            margin: 0px;
            border: none;
        """)

        title_label = QLabel("KU CubeSat")
        title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        title_label.setStyleSheet("color: white; font-size: 64px; font-family: Inter;")

        top_bar_layout = QVBoxLayout()
        top_bar_layout.setContentsMargins(25, 0, 0, 0)
        top_bar_layout.addWidget(title_label)
        top_bar.setLayout(top_bar_layout)

        return top_bar

    def createTopBarLog(self):
        top_bar = QFrame()
        top_bar.setFixedHeight(100)
        top_bar.setStyleSheet("""
            background-color: #1D3557;
            padding: 0px;
            margin: 0px;
            border: none;
        """)

        top_bar_layout = QHBoxLayout()
        top_bar_layout.setContentsMargins(25, 0, 25, 0)

        title_label = QLabel("KU CubeSat")
        title_label.setStyleSheet("color: white; font-size: 64px; font-family: Inter;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        back_button = QPushButton(top_bar)
        back_button.setFixedSize(60, 60)
        back_button.setStyleSheet("background-color: transparent; border: none;")

        icon_path = r"C:\Users\tuaok\Pictures\CS-Project\icon\arrow_back.png"
        if os.path.exists(icon_path):  
            back_button.setIcon(QIcon(icon_path))
            back_button.setIconSize(QSize(60, 60))

        back_button.clicked.connect(self.goBackToMain)

        top_bar_layout.addWidget(title_label)
        top_bar_layout.addStretch(1)
        top_bar_layout.addWidget(back_button)

        top_bar.setLayout(top_bar_layout)

        return top_bar
    
    def createTopBarPic(self):
        """✅ สร้าง Top Bar สำหรับหน้า Picture List"""
        top_bar = QFrame()
        top_bar.setFixedHeight(100)
        top_bar.setStyleSheet("""
            background-color: #1D3557;
            padding: 0px;
            margin: 0px;
            border: none;
        """)

        top_bar_layout = QHBoxLayout()
        top_bar_layout.setContentsMargins(25, 0, 25, 0)

        title_label = QLabel("KU CubeSat")
        title_label.setStyleSheet("color: white; font-size: 64px; font-family: Inter;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        back_button = QPushButton(top_bar)
        back_button.setFixedSize(60, 60)
        back_button.setStyleSheet("background-color: transparent; border: none;")

        icon_path = r"C:\Users\tuaok\Pictures\CS-Project\icon\arrow_back.png"
        if os.path.exists(icon_path):  
            back_button.setIcon(QIcon(icon_path))
            back_button.setIconSize(QSize(60, 60))

        back_button.clicked.connect(self.goBackToMain)

        top_bar_layout.addWidget(title_label)
        top_bar_layout.addStretch(1)
        top_bar_layout.addWidget(back_button)

        top_bar.setLayout(top_bar_layout)

        return top_bar
    
    def createBottomBar(self):
        self.bottom_bar = QFrame()
        self.bottom_bar.setFixedHeight(50)
        self.bottom_bar.setStyleSheet("background-color: #1D3557; padding: 0px; margin: 0px;")
        
        bottom_bar_layout = QVBoxLayout()
        self.bottom_bar.setLayout(bottom_bar_layout)

    def createMissionPlanBox(self):
        """สร้างกล่อง Mission Plan และ Upload schedule"""
        self.missionPlanLayout = QHBoxLayout()
        self.missionPlanLayout.setContentsMargins(20, 0, 0, 0)
        self.missionPlanLayout.setSpacing(20)
        self.missionPlanLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.missionPlanBox = QFrame()
        self.missionPlanBox.setFixedSize(219, 75)
        self.missionPlanBox.setStyleSheet("""
            border: 5px solid #4E82B2;
            background-color: white;
            border-radius: 30px;
            padding: 0px;
            margin: 0px;
        """)

        mission_label = QLabel("Mission Plan")
        mission_label.setStyleSheet("font-size: 24px; font-family: Inter; color: black; border: none;")
        mission_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        mission_box_layout = QVBoxLayout(self.missionPlanBox)
        mission_box_layout.setContentsMargins(0, 0, 0, 0)
        mission_box_layout.addWidget(mission_label)

        upload_section = QGridLayout()
        upload_section.setContentsMargins(0, 0, 0, 0)
        upload_section.setSpacing(10) 

        upload_label = QLabel("Upload schedule")
        upload_label.setStyleSheet("""
            font-size: 16px;
            font-family: Inter;
            color: black;
        """)
        upload_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.uploadScheduleBox = QLineEdit()
        self.uploadScheduleBox.setFixedSize(300, 36)
        self.uploadScheduleBox.setReadOnly(True) 
        self.uploadScheduleBox.setPlaceholderText("File upload...") 
        self.uploadScheduleBox.setStyleSheet("""
            border: 1px solid #000000;
            background-color: white;
        """)
        self.uploadScheduleBox.setStyleSheet("""
            font-family: Inter;
            font-size: 16px;
            color: black;
            border: 1px solid #000000;
            background-color: white;
        """)



        self.upload_button = QPushButton("Upload")
        self.upload_button.setFixedSize(110, 39)
        self.upload_button.setStyleSheet("""
            background-color: #00A3FF;
            color: #FFFFFF;
            font-size: 16px;
            border: 1px solid #000000;
            border-radius: 10px;
            padding: 5px;
        """)
        self.upload_button.clicked.connect(self.uploadFile)

        self.clear_button = QPushButton("Clear")
        self.clear_button.setFixedSize(93, 40)
        self.clear_button.setStyleSheet("""
            background-color:rgb(204, 25, 25);
            color: #FFFFFF;
            border: 1px solid #000000;
            font-size: 16px;
            border-radius: 10px;
            padding: 5px;
        """)
        self.clear_button.clicked.connect(self.clearFile)

        
        self.send_button = QPushButton("Send")
        self.send_button.setFixedSize(93, 40)
        self.send_button.setStyleSheet("""
            background-color: #55FF00;
            color: #000000;
            font-size: 16px;
            border: 1px solid #000000;
            border-radius: 10px;
            padding: 5px;
        """)
        self.send_button.clicked.connect(self.sendFile)

        
        upload_section.addWidget(upload_label, 0, 0, 3, 0)  
        upload_section.addWidget(self.uploadScheduleBox, 1, 0)  
        upload_section.addWidget(self.upload_button, 1, 1)  
        upload_section.addWidget(self.clear_button, 1, 2)
        upload_section.addWidget(self.send_button, 1, 3)  
        self.missionPlanLayout.addWidget(self.missionPlanBox)
        self.missionPlanLayout.addLayout(upload_section)

        from PyQt6.QtCore import QFileInfo

    def uploadFile(self):
        file_dialog = QFileDialog()
        
        default_path = "C:\งานตั้น\CS-Project"

        file_path, _ = file_dialog.getOpenFileName(self, "Select File", default_path, "Text Files (*.txt)")
        
        if file_path:
            file_name = QFileInfo(file_path).fileName() 
            self.uploadScheduleBox.setText(file_name) 

    def clearFile(self):
        self.uploadScheduleBox.clear() 


    from PyQt6.QtWidgets import QMessageBox

    from PyQt6.QtWidgets import QMessageBox

    def sendFile(self):
        file_name = self.uploadScheduleBox.text()

        if file_name:
            print(f"Sending file: {file_name}")
        else:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Warning)  
            msg_box.setWindowTitle("Warning")
            msg_box.setText('<span style="color:black;">No file selected</span>') 
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)  
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: white; 
                    color: black;  
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #00A3FF;
                    color: white;
                    border-radius: 5px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #008CDA; 
                }
            """)

            msg_box.exec() 
    
    def createTelecommandBox(self):
        """สร้างกล่อง Telecommand และ Module ID"""
        self.telecommandLayout = QHBoxLayout()
        self.telecommandLayout.setContentsMargins(20, 0, 0, 0)
        self.telecommandLayout.setSpacing(20)
        self.telecommandLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.telecommandBox = QFrame()
        self.telecommandBox.setFixedSize(219, 75)
        self.telecommandBox.setStyleSheet("""
            border: 5px solid #4E82B2;
            background-color: white;
            border-radius: 30px;
            padding: 0px;
            margin: 0px;
        """)

        telecommand_label = QLabel("Telecommand")
        telecommand_label.setStyleSheet("font-size: 24px; font-family: Inter; color: black; border: none;")
        telecommand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        telecommand_box_layout = QVBoxLayout(self.telecommandBox)
        telecommand_box_layout.setContentsMargins(0, 0, 0, 0)
        telecommand_box_layout.addWidget(telecommand_label)

        module_section = QGridLayout()
        module_section.setContentsMargins(0, 0, 0, 0)
        module_section.setSpacing(10)

        module_label = QLabel("Module ID")
        module_label.setStyleSheet("font-size: 16px; font-family: Inter; color: black;")
        module_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        request_label = QLabel("Request ID")
        request_label.setStyleSheet("font-size: 16px; font-family: Inter; color: black;")
        request_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        parameter_label = QLabel("Parameter")
        parameter_label.setStyleSheet("font-size: 16px; font-family: Inter; color: black;")
        parameter_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.moduleIDBox = QComboBox()
        self.moduleIDBox.setFixedSize(115, 50)
        self.moduleIDBox.setStyleSheet("border: 1px solid #000000; background-color: white; font-size: 16px; color: black;")
        self.moduleIDBox.addItems(["1", "2", "3"])  
        self.moduleIDBox.currentIndexChanged.connect(self.updateRequestIDOptions)  

        self.reqIDBox = QComboBox()
        self.reqIDBox.setFixedSize(115, 50)
        self.reqIDBox.setStyleSheet("border: 1px solid #000000; background-color: white; font-size: 16px; color: black;")

        self.paramIDBox = QLineEdit()
        self.paramIDBox.setFixedSize(115, 50)
        self.paramIDBox.setStyleSheet("border: 1px solid #000000; background-color: white; font-size: 16px; color: black;")

        self.paramIDBox.setPlaceholderText("Enter value...")

        self.paramIDBox.setValidator(QIntValidator())  

        self.sendTelecommandButton = QPushButton("Send")
        self.sendTelecommandButton.setFixedSize(93, 40)
        self.sendTelecommandButton.setStyleSheet("""
            background-color: #55FF00;
            color: #000000;
            font-size: 16px;
            border: 1px solid #000000;
            border-radius: 10px;
            padding: 5px;
        """)
        self.sendTelecommandButton.clicked.connect(self.sendTelecommand)  

        module_section.addWidget(module_label, 0, 0)  
        module_section.addWidget(self.moduleIDBox, 1, 0)  
        module_section.addWidget(request_label, 0, 1)  
        module_section.addWidget(self.reqIDBox, 1, 1)  
        module_section.addWidget(parameter_label, 0, 2)  
        module_section.addWidget(self.paramIDBox, 1, 2)  
        module_section.addWidget(self.sendTelecommandButton, 1, 3)  
        self.telecommandLayout.addWidget(self.telecommandBox)
        self.telecommandLayout.addLayout(module_section)

        self.updateRequestIDOptions()

    def updateParameterField(self):
        """ปรับเปลี่ยนช่อง Parameter ตาม Module ID และ Request ID ที่เลือก """
        module_id = int(self.moduleIDBox.currentText()) 
        
        request_text = self.reqIDBox.currentText()
        if request_text.isdigit(): 
            request_id = int(request_text)  
        else:
            return  

        disable_conditions = [
            (module_id == 1 and request_id in [1, 2, 3, 4, 5]),
            (module_id == 3 and request_id in [1, 2, 4])
        ]

        range_conditions = {
            (2, 1): (1, 30),  
            (2, 2): (1, 30),  
            (3, 3): (5, 60)   
        }

        if any(disable_conditions):
            self.paramIDBox.setReadOnly(True) 
            self.paramIDBox.setStyleSheet("""
                border: 1px solid #000000;
                background-color: #D3D3D3;
                font-size: 16px;
                color: black;
            """)
            self.paramIDBox.setText("") 
            self.paramIDBox.setValidator(None)  
        else:
            self.paramIDBox.setReadOnly(False) 
            self.paramIDBox.setStyleSheet("""
                border: 1px solid #000000;
                background-color: white;
                font-size: 16px;
                color: black;
            """)

            if (module_id, request_id) in range_conditions:
                min_val, max_val = range_conditions[(module_id, request_id)]
                self.paramIDBox.setValidator(QIntValidator(min_val, max_val))  
            else:
                self.paramIDBox.setValidator(None)  


    def updateRequestIDOptions(self):
        """อัปเดตรายการ Request ID และเรียก `updateParameterField()` เมื่อเปลี่ยนค่า"""
        module_id = int(self.moduleIDBox.currentText())  
        
        self.reqIDBox.clear()

        request_options = {
            1: ["1", "2", "3", "4", "5"],
            2: ["1", "2"],
            3: ["1", "2", "3", "4"]
        }

        self.reqIDBox.addItems(request_options.get(module_id, []))

        self.reqIDBox.currentIndexChanged.connect(self.updateParameterField)

        self.updateParameterField()

    
    def sendTelecommand(self):
        try:
            moduleID = int(self.moduleIDBox.currentText())  
            reqID = int(self.reqIDBox.currentText())  
            paramVal = int(self.paramIDBox.text())  

            valid_ranges = {
                (2, 1): (1, 30),
                (2, 2): (1, 30),
                (3, 3): (5, 60)
            }

            if (moduleID, reqID) in valid_ranges:
                min_val, max_val = valid_ranges[(moduleID, reqID)]
                if not (min_val <= paramVal <= max_val):
                    raise ValueError(f"⚠️ Parameter out of range! (Allowed: {min_val} - {max_val})")

            print(f"📡 Sending Telecommand -> Module ID: {moduleID}, Req ID: {reqID}, Parameter: {paramVal}")

            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("Telecommand Sent")
            msg_box.setText(f"✅ Sent Telecommand:\nModule ID: {moduleID}\nReq ID: {reqID}\nParameter: {paramVal}")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()

        except ValueError as e:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("Input Error")
            msg_box.setText(str(e))
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()


    def createTelemetryBox(self):
        """สร้างกล่อง Telemetry และ Module ID"""
        self.telemetryLayout = QHBoxLayout()
        self.telemetryLayout.setContentsMargins(20, 0, 0, 0)
        self.telemetryLayout.setSpacing(20)
        self.telemetryLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.telemetryBox = QFrame()
        self.telemetryBox.setFixedSize(219, 75)
        self.telemetryBox.setStyleSheet("""
            border: 5px solid #4E82B2;
            background-color: white;
            border-radius: 30px;
            padding: 0px;
            margin: 0px;
        """)

        telemetry_label = QLabel("Telemetry")
        telemetry_label.setStyleSheet("font-size: 24px; font-family: Inter; color: black; border: none;")
        telemetry_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        telemetry_box_layout = QVBoxLayout(self.telemetryBox)
        telemetry_box_layout.setContentsMargins(0, 0, 0, 0)
        telemetry_box_layout.addWidget(telemetry_label)

        telemetry_section = QGridLayout()
        telemetry_section.setContentsMargins(0, 0, 0, 0)
        telemetry_section.setSpacing(10)

        module_label = QLabel("Module ID")
        module_label.setStyleSheet("font-size: 16px; font-family: Inter; color: black;")
        module_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        request_label = QLabel("Request ID")
        request_label.setStyleSheet("font-size: 16px; font-family: Inter; color: black;")
        request_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        value_label = QLabel("Value")
        value_label.setStyleSheet("font-size: 16px; font-family: Inter; color: black;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.moduleTelemetryBox = QComboBox()
        self.moduleTelemetryBox.setFixedSize(115, 50)
        self.moduleTelemetryBox.setStyleSheet("border: 1px solid #000000; background-color: white; font-size: 16px; color: black;")
        self.moduleTelemetryBox.addItems(["1", "2", "3"]) 
        self.moduleTelemetryBox.currentIndexChanged.connect(self.updateRequestIDTelemetryOptions) 

        self.reqTelemetryBox = QComboBox()
        self.reqTelemetryBox.setFixedSize(115, 50)
        self.reqTelemetryBox.setStyleSheet("border: 1px solid #000000; background-color: white; font-size: 16px; color: black;")

        self.valueTelemetryLabel = QLabel("") 
        self.valueTelemetryLabel.setFixedSize(115, 50)
        self.valueTelemetryLabel.setStyleSheet("""
            border: 1px solid #000000;
            background-color: #F0F0F0;
            font-size: 16px;
            color: black;
            padding: 5px;
        """)
        self.valueTelemetryLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.sendTelemetryButton = QPushButton("Send")
        self.sendTelemetryButton.setFixedSize(93, 40)
        self.sendTelemetryButton.setStyleSheet("""
            background-color: #55FF00;
            color: #000000;
            font-size: 16px;
            border: 1px solid #000000;
            border-radius: 10px;
            padding: 5px;
        """)
        self.sendTelemetryButton.clicked.connect(self.sendTelemetry) 

        telemetry_section.addWidget(module_label, 0, 0)
        telemetry_section.addWidget(self.moduleTelemetryBox, 1, 0)  
        telemetry_section.addWidget(request_label, 0, 1)  
        telemetry_section.addWidget(self.reqTelemetryBox, 1, 1)  
        telemetry_section.addWidget(value_label, 0, 3)  
        telemetry_section.addWidget(self.valueTelemetryLabel, 1, 3)  
        telemetry_section.addWidget(self.sendTelemetryButton, 1, 2)  
        self.telemetryLayout.addWidget(self.telemetryBox)
        self.telemetryLayout.addLayout(telemetry_section)
        
        self.updateRequestIDTelemetryOptions()

    def updateRequestIDTelemetryOptions(self):
        """อัปเดตรายการ Request ID ของ Telemetry ตาม Module ID ที่เลือก"""
        module_id = int(self.moduleTelemetryBox.currentText()) 

        self.reqTelemetryBox.clear()

        request_options = {
            1: ["1", "2", "3", "4", "5"],
            2: ["1", "2", "3", "4", "5", "6"],
            3: ["1", "2", "3", "4", "5"]
        }

        self.reqTelemetryBox.addItems(request_options.get(module_id, []))

    def sendTelemetry(self):
        """ฟังก์ชันส่งข้อมูล Telemetry"""
        try:
            moduleID = int(self.moduleTelemetryBox.currentText()) 
            reqID = int(self.reqTelemetryBox.currentText())
            value = int(self.valueTelemetryLabel.text())  

            print(f"📡 Sending Telemetry -> Module ID: {moduleID}, Request ID: {reqID}")

            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("Telemetry Sent")
            msg_box.setText(f"✅ Sent Telemetry:\nModule ID: {moduleID}\nRequest ID: {reqID}")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()

        except ValueError:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("Input Error")
            msg_box.setText("⚠️ Invalid input! Please enter a valid number.")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()


    def updateTelemetryValue(self, new_value):
        """ฟังก์ชันรับค่าจากเซ็นเซอร์ หรือ API แล้วอัปเดต Value"""
        self.valueTelemetryLabel.setText(str(new_value))  
    
    def createPayloadTM(self):
        """สร้างกรอบ Payload Status สำหรับรับค่าจากภายนอก"""
        self.payloadLayout = QHBoxLayout()
        self.payloadLayout.setContentsMargins(20, 0, 0, 0)
        self.payloadLayout.setSpacing(20)
        self.payloadLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.payloadBox = QFrame()
        self.payloadBox.setFixedSize(219, 75)
        self.payloadBox.setStyleSheet("""
            border: 5px solid #4E82B2;
            background-color: white;
            border-radius: 30px;
            padding: 0px;
            margin: 0px;
        """)

        payload_label = QLabel("Payload")
        payload_label.setStyleSheet("font-size: 24px; font-family: Inter; color: black; border: none;")
        payload_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        payload_box_layout = QVBoxLayout(self.payloadBox)
        payload_box_layout.setContentsMargins(0, 0, 0, 0)
        payload_box_layout.addWidget(payload_label)

        payload_section = QGridLayout()
        payload_section.setContentsMargins(0, 0, 0, 0)
        payload_section.setSpacing(10)

        plstatus_label = QLabel("Payload Status")
        plstatus_label.setStyleSheet("font-size: 16px; font-family: Inter; color: black;")
        plstatus_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.valuePayloadLabel = QLabel("") 
        self.valuePayloadLabel.setFixedSize(150, 50)
        self.valuePayloadLabel.setStyleSheet("""
            border: 1px solid #000000;
            background-color: #F0F0F0;
            font-size: 16px;
            color: black;
            padding: 5px;
        """)
        self.valuePayloadLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        payload_section.addWidget(plstatus_label, 0, 0)  
        payload_section.addWidget(self.valuePayloadLabel, 1, 0) 


        #payload_box_layout.addLayout(payload_section) 
        self.payloadLayout.addWidget(self.payloadBox)
        self.payloadLayout.addLayout(payload_section)
        


    def updatePayloadStatus(self, new_status):
        """ฟังก์ชันรับค่าจากภายนอกแล้วอัปเดตช่อง Payload"""
        self.payloadStatusInput.setText(str(new_status))


    def createfswTM(self):
        self.fswLayout = QHBoxLayout()
        self.fswLayout.setContentsMargins(20, 0, 0, 0)
        self.fswLayout.setSpacing(20)
        self.fswLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.fswBox = QFrame()
        self.fswBox.setFixedSize(219, 75)
        self.fswBox.setStyleSheet("""
            border: 5px solid #4E82B2;
            background-color: white;
            border-radius: 30px;
            padding: 0px;
            margin: 0px;
        """)

        fsw_label = QLabel("Flight Software")
        fsw_label.setStyleSheet("font-size: 24px; font-family: Inter; color: black; border: none;")
        fsw_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        fsw_box_layout = QVBoxLayout(self.fswBox)
        fsw_box_layout.setContentsMargins(0, 0, 0, 0)
        fsw_box_layout.addWidget(fsw_label)

        fsw_section = QGridLayout()
        fsw_section.setContentsMargins(0, 0, 0, 0)
        fsw_section.setSpacing(10)
        # Memory Usage Layout
        mu_label = QLabel("Memory Usage")
        mu_label.setStyleSheet("font-size: 16px; font-family: Inter; color: black;")
        mu_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.valueMuLabel = QLabel("")
        self.valueMuLabel.setFixedSize(150, 50)
        self.valueMuLabel.setStyleSheet("""
            border: 1px solid #000000;
            background-color: #FFFFFF;
            font-size: 16px;
            color: black;
            padding: 5px;
        """)
        self.valueMuLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Memory Remain Layout
        mr_label = QLabel("Memory Remain")
        mr_label.setStyleSheet("font-size: 16px; font-family: Inter; color: black;")
        mr_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.valueMrLabel = QLabel("")
        self.valueMrLabel.setFixedSize(150, 50)
        self.valueMrLabel.setStyleSheet("""
            border: 1px solid #000000;
            background-color: #FFFFFF;
            font-size: 16px;
            color: black;
            padding: 5px;
        """)
        self.valueMrLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # FSW OBC Time Layout
        OBC_label = QLabel("OBC Time")
        OBC_label.setStyleSheet("font-size: 16px; font-family: Inter; color: black;")
        OBC_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.valueOBCLabel = QLabel("")
        self.valueOBCLabel.setFixedSize(150, 50)
        self.valueOBCLabel.setStyleSheet("""
            border: 1px solid #000000;
            background-color: #FFFFFF;
            font-size: 16px;
            color: black;
            padding: 5px;
        """)
        self.valueOBCLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        fsw_section.addWidget(mu_label, 0, 0)  
        fsw_section.addWidget(self.valueMuLabel, 1, 0)
        fsw_section.addWidget(mr_label, 0, 1)
        fsw_section.addWidget(self.valueMrLabel, 1, 1)
        fsw_section.addWidget(OBC_label, 0, 2)
        fsw_section.addWidget(self.valueOBCLabel, 1, 2)

        self.fswLayout.addWidget(self.fswBox)
        self.fswLayout.addLayout(fsw_section)

    def createGPSTM(self):
        self.GPSLayout = QHBoxLayout()
        self.GPSLayout.setContentsMargins(20, 0, 0, 0)
        self.GPSLayout.setSpacing(20)
        self.GPSLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.GPSBOX = QFrame()
        self.GPSBOX.setFixedSize(219, 75)
        self.GPSBOX.setStyleSheet("""
            border: 5px solid #4E82B2;
            background-color: white;
            border-radius: 30px;
            padding: 0px;
            margin: 0px;
        """)

        GPS_label = QLabel("GPS")
        GPS_label.setStyleSheet("font-size: 24px; font-family: Inter; color: black; border: none;")
        GPS_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        GPS_box_layout = QVBoxLayout(self.GPSBOX)
        GPS_box_layout.setContentsMargins(0, 0, 0, 0)
        GPS_box_layout.addWidget(GPS_label)

        gps_section = QGridLayout()
        gps_section.setContentsMargins(0, 0, 0, 0)
        gps_section.setSpacing(10)

        # GPS Time Layout
        gpsstatus_label = QLabel("GPS Status")
        gpsstatus_label.setStyleSheet("font-size: 16px; font-family: Inter; color: black;")
        gpsstatus_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.valueGPSstatusLabel = QLabel("")
        self.valueGPSstatusLabel.setFixedSize(150, 50)
        self.valueGPSstatusLabel.setStyleSheet("""
            border: 1px solid #000000;
            background-color: #FFFFFF;
            font-size: 16px;
            color: black;
            padding: 5px;
        """)
        self.valueGPSstatusLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # GPS Time Layout
        latitude_label = QLabel("Latitude")
        latitude_label.setStyleSheet("font-size: 16px; font-family: Inter; color: black;")
        latitude_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.valueLatitudeLabel = QLabel("")
        self.valueLatitudeLabel.setFixedSize(150, 50)
        self.valueLatitudeLabel.setStyleSheet("""
            border: 1px solid #000000;
            background-color: #FFFFFF;
            font-size: 16px;
            color: black;
            padding: 5px;
        """)
        self.valueLatitudeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # GPS Time Layout
        longitude_label = QLabel("Longitude")
        longitude_label.setStyleSheet("font-size: 16px; font-family: Inter; color: black;")
        longitude_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.valueLongitudeLabel = QLabel("")
        self.valueLongitudeLabel.setFixedSize(150, 50)
        self.valueLongitudeLabel.setStyleSheet("""
            border: 1px solid #000000;
            background-color: #FFFFFF;
            font-size: 16px;
            color: black;
            padding: 5px;
        """)
        self.valueLongitudeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        gps_section.addWidget(gpsstatus_label, 0, 0)  
        gps_section.addWidget(self.valueGPSstatusLabel, 1, 0)
        gps_section.addWidget(latitude_label, 0, 1)  
        gps_section.addWidget(self.valueLatitudeLabel, 1, 1)
        gps_section.addWidget(longitude_label, 0, 2)  
        gps_section.addWidget(self.valueLongitudeLabel, 1, 2)

        self.GPSLayout.addWidget(self.GPSBOX)
        self.GPSLayout.addLayout(gps_section)

    def get_latest_image(self):
        """ 🔹 ดึงไฟล์รูปภาพล่าสุดจากโฟลเดอร์ """
        if not os.path.exists(self.image_folder):
            return None  # หากโฟลเดอร์ไม่ถูกต้อง

        files = [f for f in os.listdir(self.image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        if not files:
            return None  # ไม่มีไฟล์ภาพในโฟลเดอร์

        # เรียงลำดับตามเวลาแก้ไขล่าสุด (mtime)
        files.sort(key=lambda x: os.path.getmtime(os.path.join(self.image_folder, x)), reverse=True)
        return os.path.join(self.image_folder, files[0])

    def uploadLatestImage(self):
        """ 🔹 โหลดรูปภาพล่าสุดและแสดงบน QLabel """
        latest_image = self.get_latest_image()
        if latest_image:
            pixmap = QPixmap(latest_image).scaled(550, 380)
            self.image_frame.setPixmap(pixmap)  # แสดงภาพ
            self.image_frame.setStyleSheet("border: 2px solid black; background-color: white;")
        else:
            self.image_frame.setText("โปรดรอรูปภาพ...")  # แสดงข้อความหากไม่มีรูป
            self.image_frame.setStyleSheet("""
                border: 2px solid black;
                background-color: white;
                font-size: 18px;
                color: gray;
            """)

    def openLogFilePage(self):
        self.stack.setCurrentWidget(self.logFileWidget) 

    def goBackToMain(self):
        self.stack.setCurrentWidget(self.mainWidget)

    def openPictureList(self):
        self.stack.setCurrentWidget(self.picWidget)

    def initLogFileUI(self):
        layout = QVBoxLayout(self.logFileWidget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.top_bar_log)
        layout.addWidget(self.top_bar_log, alignment=Qt.AlignmentFlag.AlignTop)

        table_layout = QVBoxLayout()
        table_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.createLogFileLabel()
        self.createLogTable()
        self.createClearLogButton()

        layout.addLayout(table_layout)
        self.loadLogFiles()

        self.log_refresh_timer = QTimer(self)
        self.log_refresh_timer.timeout.connect(self.loadLogFiles)
        self.log_refresh_timer.start(0) 

        self.cleared_files = set() 
        
    def createLogFileLabel(self):
        self.log_file_button = QPushButton("Log File", self.logFileWidget)
        self.log_file_button.setFixedSize(150, 75)
        self.log_file_button.setStyleSheet("""
            border: 5px solid #4E82B2;
            background-color: white;
            font-size: 24px;
            border-radius: 30px;
        """)
        self.log_file_button.move(50, 120) 

    def createLogTable(self):
        self.scroll_area = QScrollArea(self.logFileWidget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedSize(770, 450)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.log_table = QTableWidget()
        self.log_table.setColumnCount(3)
        self.log_table.setHorizontalHeaderLabels(["Log Name", "Detail", "Delete"])
        self.log_table.setColumnWidth(0, 350)
        self.log_table.setColumnWidth(1, 200)
        self.log_table.setColumnWidth(2, 200)
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.log_table.verticalHeader().setVisible(False)
        self.log_table.setRowCount(15)
        for row in range(15):
            self.log_table.setRowHeight(row, 30)

        self.log_table.setStyleSheet("""
            QTableWidget {
                font-size: 16px;
                color: black;
                background-color: white;
                gridline-color: black;
                border: 1px solid black;
            }
            QHeaderView::section {
                background-color: #E0E0E0;
                font-size: 16px;
                font-weight: bold;
                border: 1px solid black;
            }
            QTableWidget::item {
                border: 1px solid black;
            }
        """)
        self.scroll_area.move(430, 200)
        self.scroll_area.setWidget(self.log_table)

    def createClearLogButton(self):
        """✅ สร้างปุ่ม Clear Data"""
        self.clear_button = QPushButton("Clear Data", self.logFileWidget)
        self.clear_button.setFixedSize(180, 60)
        self.clear_button.setStyleSheet("""
            background-color: red;
            color: white;
            font-size: 18px;
            font-weight: bold;
            border-radius: 10px;
        """)
        self.clear_button.clicked.connect(self.clearLogFiles)
        self.clear_button.move(1020, 675) 

    def loadLogFiles(self, *arg):
        folder_path = r"C:\Tun\GUI_project\Log_File"

        if not os.path.exists(folder_path):
            QMessageBox.critical(self, "Error", f"❌ Folder not found: {folder_path}")
            return

        files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
        files = [f for f in files if f not in self.cleared_files]
        files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(folder_path, x)), reverse=True)

        min_rows = 15
        row_count = max(len(files), min_rows)

        self.log_table.setRowCount(row_count) 

        if hasattr(self, "loaded_files") and self.loaded_files == files:
            return

        self.loaded_files = files

        for row in range(row_count):
            if row < len(files):
                file_name = files[row]
                file_path = os.path.join(folder_path, file_name)
                
                log_item = QTableWidgetItem(file_name)
                self.log_table.setItem(row, 0, log_item)

                detail_button = QPushButton("Open File")
                detail_button.setStyleSheet("color: blue; background-color: transparent; border: none; text-decoration: underline;")
                detail_button.clicked.connect(lambda checked=False, path=file_path: self.openLogFile(path))
                self.log_table.setCellWidget(row, 1, detail_button)

                delete_button = QPushButton("Delete")
                delete_button.setStyleSheet("color: red; background-color: transparent; border: none; text-decoration: underline;")
                delete_button.clicked.connect(lambda checked=False, path=file_path: self.deleteLogFile(path))
                self.log_table.setCellWidget(row, 2, delete_button)
                
            else:
                self.log_table.setItem(row, 0, QTableWidgetItem("")) 
                self.log_table.setCellWidget(row, 1, QLabel("")) 
                self.log_table.setCellWidget(row, 2, QLabel("")) 

    def openLogFile(self, file_path):
        try:
            file_path = os.path.abspath(file_path)  
            print(f"🔍 Opening File: {file_path}")

            if not os.path.exists(file_path):
                QMessageBox.critical(self, "Error", f"❌ File not found: {file_path}")
                return

            os.startfile(file_path) 

        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Failed to open file: {str(e)}")

    def deleteLogFile(self, file_path, checked=False):
        reply = QMessageBox.question(self, "Delete Log", f"❌ Do you want to delete {os.path.basename(file_path)}?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                os.remove(file_path)
                self.loadLogFiles()
                QMessageBox.information(self, "Deleted", f"🗑️ {os.path.basename(file_path)} has been deleted.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"❌ Failed to delete file: {str(e)}")

    def clearLogFiles(self):
        reply = QMessageBox.question(self, "Archive Data",
                                    "⚠️ Do you want to archive and clear all log files?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            folder_path = r"C:\Tun\GUI_project\Log_File"  
            archive_folder = r"C:\Tun\GUI_project\Clear_Data"  
            os.makedirs(archive_folder, exist_ok=True) 

            date_str = datetime.datetime.now().strftime("%Y%m%d")  

            existing_zip_files = [f for f in os.listdir(archive_folder) if f.startswith(f"Log_Data_{date_str}") and f.endswith(".zip")]
            next_index = len(existing_zip_files) + 1 

            archive_name = f"Log_Data_{date_str}_{next_index}.zip"
            archive_path = os.path.join(archive_folder, archive_name)

            log_files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
            
            if not log_files:
                QMessageBox.warning(self, "No Files", "⚠️ No log files found to archive.")
                return  

            deleted_files = []  
            try:
                with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_name in log_files:
                        file_path = os.path.join(folder_path, file_name)
                        if os.path.isfile(file_path):  
                            zipf.write(file_path, arcname=file_name)  
                            deleted_files.append(file_path)  

                if os.path.exists(archive_path):
                    for file_path in deleted_files:
                        try:
                            os.remove(file_path)
                        except Exception as e:
                            print(f"❌ Failed to delete {file_path}: {e}")
                            
                else:
                    QMessageBox.critical(self, "Error", "❌ Failed to create ZIP file.")
                    return

            except Exception as e:
                QMessageBox.critical(self, "Error", f"❌ ZIP Archive Error: {e}")
                return

            row_count = self.log_table.rowCount()
            for row in range(row_count):
                self.log_table.setItem(row, 0, QTableWidgetItem(""))  
                self.log_table.setCellWidget(row, 1, None)  
                self.log_table.setCellWidget(row, 2, None)  

            QMessageBox.information(self, "Archived", f"📂 All log files have been archived and deleted:\n{archive_path}")

    def initPictureListUI(self):
        layout = QVBoxLayout(self.picWidget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.top_bar_pic)
        layout.addWidget(self.top_bar_pic, alignment=Qt.AlignmentFlag.AlignTop)

        table_layout = QVBoxLayout()
        table_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.createPicFileLabel()
        self.createPicTable()
        self.createClearPicButton()

        layout.addLayout(table_layout)
        self.loadPicFiles()
        
        self.pic_refresh_timer = QTimer(self)
        self.pic_refresh_timer.timeout.connect(self.loadPicFiles)
        self.pic_refresh_timer.start(0)  

        self.cleared_files_pic = set() 

    def createPicFileLabel(self):
        self.pic_file_button = QPushButton("Picture List", self.picWidget)
        self.pic_file_button.setFixedSize(150, 75)
        self.pic_file_button.setStyleSheet("""
            border: 5px solid #4E82B2;
            background-color: white;
            font-size: 24px;
            border-radius: 30px;
        """)
        self.pic_file_button.move(50, 120)  

    def createPicTable(self):
        self.scroll_area = QScrollArea(self.picWidget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedSize(770, 450)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.Pic_table = QTableWidget()
        self.Pic_table.setColumnCount(3)
        self.Pic_table.setHorizontalHeaderLabels(["Picture Name", "Detail", "Delete"])
        
        self.Pic_table.setColumnWidth(0, 350)
        self.Pic_table.setColumnWidth(1, 200)
        self.Pic_table.setColumnWidth(2, 200)

        self.Pic_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.Pic_table.verticalHeader().setVisible(False)
        
        self.Pic_table.setRowCount(15)
        for row in range(15):
            self.Pic_table.setRowHeight(row, 30)
            
        self.Pic_table.setStyleSheet("""
            QTableWidget {
                font-size: 16px;
                color: black;
                background-color: white;
                gridline-color: black;
                border: 1px solid black;
            }
            QHeaderView::section {
                background-color: #E0E0E0;
                font-size: 16px;
                font-weight: bold;
                border: 1px solid black;
            }
            QTableWidget::item {
                border: 1px solid black;
            }
        """)
        self.scroll_area.move(430, 200)
        self.scroll_area.setWidget(self.Pic_table)

    def createClearPicButton(self):
        """✅ สร้างปุ่ม Clear Data"""
        self.clear_button = QPushButton("Clear Data", self.picWidget)
        self.clear_button.setFixedSize(180, 60)
        self.clear_button.setStyleSheet("""
            background-color: red;
            color: white;
            font-size: 18px;
            font-weight: bold;
            border-radius: 10px;
        """)
        self.clear_button.clicked.connect(self.clearPicFiles)
        self.clear_button.move(1020, 675) 
    
    def loadPicFiles(self, *arg):
        folder_path = r"C:\Users\tuaok\Pictures\CS-Project"
        
        if not os.path.exists(folder_path):
            QMessageBox.critical(self, "Error", f"❌ Folder not found: {folder_path}")
            return

        files = [f for f in os.listdir(folder_path) if f.lower().endswith((".png", ".jpg"))]
        files = [f for f in files if f not in self.cleared_files]
        files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(folder_path, x)), reverse=True)

        min_rows = 15
        row_count = max(len(files), min_rows) 

        self.Pic_table.setRowCount(row_count) 

        if hasattr(self, "loaded_files_Pic") and self.loaded_files_Pic == files:
            return

        self.loaded_files_Pic = files

        for row in range(row_count):
            if row < len(files):
                file_name = files[row]
                file_path = os.path.join(folder_path, file_name)
                pic_item = QTableWidgetItem(file_name)
                self.Pic_table.setItem(row, 0, pic_item)

                detail_button = QPushButton("Open Picture")
                detail_button.setStyleSheet("color: blue; background-color: transparent; border: none; text-decoration: underline;")
                detail_button.clicked.connect(lambda checked=False, path=file_path: self.openPicFile(path))
                self.Pic_table.setCellWidget(row, 1, detail_button)

                delete_button = QPushButton("Delete")
                delete_button.setStyleSheet("color: red; background-color: transparent; border: none; text-decoration: underline;")
                delete_button.clicked.connect(lambda checked=False, path=file_path: self.deletePicFile(path))
                self.Pic_table.setCellWidget(row, 2, delete_button)
            else:
                self.Pic_table.setItem(row, 0, QTableWidgetItem(""))  
                self.Pic_table.setCellWidget(row, 1, QLabel(""))  
                self.Pic_table.setCellWidget(row, 2, QLabel(""))  

    def openPicFile(self, file_path):
        print("✅ ฟังก์ชัน openPicFile ถูกเรียกใช้งาน!") 
        print(f"🔍 File path received: {file_path}")  

        try:
            file_path = os.path.normpath(file_path)  
            print(f"🔍 Opening File: {file_path}") 
            
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                return

            if os.name == 'nt':  
                subprocess.Popen(["start", "", file_path], shell=True)

        except Exception as e:
            print(f"❌ Failed to open file: {str(e)}")

    def deletePicFile(self, file_path, checked=False):
        print("Hello Python - Delete") 
        print(f"🔍 File to delete: {file_path}") 

        reply = QMessageBox.question(self, "Delete Picture", f"❌ Do you want to delete {os.path.basename(file_path)}?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                os.remove(file_path)
                self.loadPicFiles()
                QMessageBox.information(self, "Deleted", f"🗑️ {os.path.basename(file_path)} has been deleted.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"❌ Failed to delete file: {str(e)}")

    
    def clearPicFiles(self):
        reply = QMessageBox.question(self, "Archive Data",
                                    "⚠️ Do you want to archive and clear all picture files?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            folder_Pic_path = r"C:\Users\tuaok\Pictures\CS-Project" 
            archive_folder_Pic = r"C:\Users\tuaok\Pictures\CS-Project\Picture_Log"  
            os.makedirs(archive_folder_Pic, exist_ok=True) 

            date_str = datetime.datetime.now().strftime("%Y%m%d") 

            existing_zip_files = [f for f in os.listdir(archive_folder_Pic) if f.startswith(f"Picture_Data_{date_str}") and f.endswith(".zip")]
            next_index = len(existing_zip_files) + 1  

            archive_name = f"Picture_Data_{date_str}_{next_index}.zip"
            archive_path = os.path.join(archive_folder_Pic, archive_name)

            pic_files = [f for f in os.listdir(folder_Pic_path) if f.endswith((".png", ".jpg"))]
            
            if not pic_files:
                QMessageBox.warning(self, "No Files", "⚠️ No picture files found to archive.")
                return  

            deleted_files = []  
            try:
                with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_name in pic_files:
                        file_path = os.path.join(folder_Pic_path, file_name)
                        if os.path.isfile(file_path): 
                            zipf.write(file_path, arcname=file_name) 
                            deleted_files.append(file_path)

                if os.path.exists(archive_path):
                    for file_path in deleted_files:
                        try:
                            os.remove(file_path)
                        except Exception as e:
                            print(f"❌ Failed to delete {file_path}: {e}")
                else:
                    QMessageBox.critical(self, "Error", "❌ Failed to create ZIP file.")
                    return

            except Exception as e:
                QMessageBox.critical(self, "Error", f"❌ ZIP Archive Error: {e}")
                return  

            row_count = self.Pic_table.rowCount()
            for row in range(row_count):
                self.Pic_table.setItem(row, 0, QTableWidgetItem(""))  
                self.Pic_table.setCellWidget(row, 1, None) 
                self.Pic_table.setCellWidget(row, 2, None)  

            QMessageBox.information(self, "Archived", f"📂 All picture files have been archived and deleted:\n{archive_path}")

app = QApplication([])
window = CubeSatGUI()
window.show()
app.exec()