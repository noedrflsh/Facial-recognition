import sys
import os
import cv2
import numpy as np
import face_recognition
from datetime import datetime

import sqlite3
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QFileDialog, QMessageBox, QFormLayout, QComboBox,QTableWidget, QTableWidgetItem,QStackedWidget

# Database initialization

def init_db():
    try:
        conn = sqlite3.connect('student_details.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS students(
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                usn TEXT NOT NULL,
                sem TEXT NOT NULL,
                branch TEXT NOT NULL,
                image BLOB NOT NULL
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                usn TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                date TEXT NOT NULL,
                month Text NOT NULL,
                login_time TEXT NOT NULL,
                logout_time TEXT NOT NULL
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

class StyleContainer:   

    def button_style(self):
        return """
            QPushButton {
                background-color: #0F0B62;
                color: #FFFBEE;
                font-family: Arial, sans-serif;  /* Specify a readable font family */
                font-size: 16px;
                padding: 10px;
                margin: 10px;
                border-radius: 10px;
                border: none;
                min-width: 140px;
                max-width: 140px;
                min-height: 20px;
                max-height: 20px;
            }
            QPushButton:hover {
                background-color: #000D2E;
            }
            QPushButton:pressed {
                background-color: #15007B;
            }
        """

    def window_style(self):
        return """
            QWidget {
                background-color: #E1DCC;
            }
        """
        
## ADMIN FILL THE FORM WITH STUDENT DETAILS LIKE USN,NAME,SEM,BRANCH AND PHOTO
class FormWindow(QMainWindow, StyleContainer):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Student Form')
        self.setGeometry(100, 100, 800, 800)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.central_widget.setStyleSheet("QWidget { " + self.window_style() + " }")
        
        self.heading_label = QLabel('Student Details')
        self.heading_label.setAlignment(Qt.AlignCenter)
        self.heading_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 20px; margin-bottom: 20px;")
        self.layout.addWidget(self.heading_label)

        # Create the form layout
        self.form_layout = QFormLayout()

        # Student Name input
        self.student_name_label = QLabel('Student Name:')
        self.student_name_input = QLineEdit(self)
        self.form_layout.addRow(self.student_name_label,self.student_name_input)

        # USN input
        self.usn_label = QLabel('USN:')
        self.usn_input = QLineEdit(self)
        self.form_layout.addRow(self.usn_label, self.usn_input)

        # Semester input
        self.sem_label = QLabel('Semester:')
        self.sem_input = QComboBox(self)
        self.sem_input.addItems(['1', '2', '3', '4', '5', '6', '7', '8'])
        self.form_layout.addRow(self.sem_label, self.sem_input)

        # Branch input
        self.branch_label = QLabel('Branch:')
        self.branch_input = QLineEdit(self)
        self.form_layout.addRow(self.branch_label, self.branch_input)

        # File input for image
        self.file_button = QPushButton('Add Image', self)
        self.file_button.clicked.connect(self.open_file_dialog)
        self.file_button.setStyleSheet(self.button_style())
        self.file_label = QLabel('No file selected')
        self.form_layout.addRow(self.file_button, self.file_label)

        # Submit button
        self.submit_button = QPushButton('Submit', self)
        self.submit_button.clicked.connect(self.submit_form)
        self.submit_button.setStyleSheet(self.button_style())
        self.form_layout.addRow(self.submit_button)
        self.layout.addLayout(self.form_layout)
        self.selected_file = None

    def open_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Image File", "", "Images (*.png *.xpm *.jpg *.jpeg);;All Files (*)", options=options)
        if file_name:
            self.selected_file = file_name
            self.file_label.setText(os.path.basename(file_name))

    def submit_form(self):
        student_name = self.student_name_input.text()
        usn = self.usn_input.text()
        sem = self.sem_input.currentText()
        branch = self.branch_input.text()
        file_path = self.selected_file

        if not student_name or not usn or not sem or not branch or not file_path:
            QMessageBox.warning(self, 'Incomplete Form', 'Please fill all fields and select a file.')
        else:
            image=cv2.imread(self.selected_file)
            path=rf'C:\Stuff\Documents\College\Mini projects\Facial recognition\images\{student_name}_{usn}.jpg'
            cv2.imwrite(path,image)
            try:
                with open(file_path, 'rb') as file:
                    image_data = file.read()

                conn = sqlite3.connect('student_details.db')
                c = conn.cursor()
                c.execute('''
                    INSERT INTO students (name, usn, sem, branch, image)
                    VALUES (?, ?, ?, ?, ?)
                ''', (student_name, usn, sem, branch, image_data))
                conn.commit()
                QMessageBox.information(self, 'Form Submitted', 'Student details have been submitted successfully.')
                self.student_name_input.clear()
                self.usn_input.clear()
                self.branch_input.clear()
                self.file_label.setText('No file selected')
                self.selected_file = None
                self.close()
            except sqlite3.Error as e:
                print(f"Database error: {e}")
                QMessageBox.critical(self, 'Database Error', 'There was an error while saving the data. Please try again.')
            finally:
                conn.close()

## ADMIN LOGIN PAGE 

class admin_login(QMainWindow, StyleContainer):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('admin Window')
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        self.heading_label = QLabel('Admin Login')
        self.heading_label.setAlignment(Qt.AlignCenter)
        self.heading_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 20px; margin-bottom: 20px;")
        self.layout.addWidget(self.heading_label)
        
        self.form_layout = QFormLayout()

        # USER Name input
        self.admin_username_label = QLabel('User Name:')
        self.admin_username_input = QLineEdit(self)
        self.admin_username_input.setStyleSheet("font-size: 14px;")  # Set font size for QLineEdit
        self.form_layout.addRow(self.admin_username_label, self.admin_username_input)

        # PASSWORD input
        self.password_label = QLabel('Password:')
        self.password_input = QLineEdit(self)
        self.password_input.setStyleSheet("font-size: 14px;")  # Set font size for QLineEdit
        self.password_input.setEchoMode(QLineEdit.Password)  # Mask password input
        self.form_layout.addRow(self.password_label, self.password_input)

        # SUBMIT BUTTON
        self.submit_button = QPushButton('Submit', self)
        self.submit_button.clicked.connect(self.check_form)
        self.submit_button.setStyleSheet(self.button_style())
        self.form_layout.addRow('', self.submit_button)  # Add empty label for button alignment

        # Align submit button to the right
        self.form_layout.setHorizontalSpacing(10)  # Adjust horizontal spacing between fields and button
        self.form_layout.setAlignment(Qt.AlignRight)  # Align elements to the right

        self.layout.addLayout(self.form_layout)

    def check_form(self):
        username = self.admin_username_input.text()
        password = self.password_input.text()
        if username == 'cse' and password == '123':
            QMessageBox.information(self, 'Confirmation', 'Login Successful')
            self.admin_username_input.clear()
            self.password_input.clear()
            self.close()
            self.a = admin_home()
            self.a.show()
        elif username == '' or password == '':
            QMessageBox.warning(self, 'Warning', 'Please fill all fields.')
        else:
            QMessageBox.information(self, 'Information', 'Incorrect username or password. Please try again.')

## ADMIN HOME PAGE
class admin_home(QWidget, StyleContainer):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background-color: #E1DCC8;")
        
        self.heading_label = QLabel('Admin Dashboard')
        self.heading_label.setAlignment(Qt.AlignCenter)
        self.heading_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 20px; margin-bottom: 20px;")
        self.layout.addWidget(self.heading_label)
        
        self.list_button = QPushButton('Attendence List', self)
        self.layout.addWidget(self.list_button)
        self.list_button.clicked.connect(self.open_list)
        self.list_button.setStyleSheet(self.button_style())
        
        self.logout_button = QPushButton('Logout', self)
        self.layout.addWidget(self.logout_button)
        self.logout_button.clicked.connect(self.open_logout)
        self.logout_button.setStyleSheet(self.button_style())
        
        self.form_button = QPushButton('Fill the Form', self)
        self.form_button.clicked.connect(self.open_form)
        self.layout.addWidget(self.form_button)
        self.form_button.setStyleSheet(self.button_style())
        
        self.setLayout(self.layout)
        self.setWindowTitle('Admin Window')
        self.setGeometry(100, 100, 800, 600)
    
    def open_form(self):
        self.form_window = FormWindow()
        self.form_window.show()
    
    def open_list(self):
        self.list_window=Table_list()
        self.list_window.show()

    def open_logout(self):
        self.close()
 
 ## MINIPROJECT HOME PAGE    
class MainWindow(QMainWindow, StyleContainer):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Main Window')
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.central_widget.setStyleSheet("QWidget { " + self.window_style() + " }")
        
        self.heading_label = QLabel('Attendance Management System')
        self.heading_label.setAlignment(Qt.AlignCenter)
        self.heading_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 20px; margin-bottom: 20px;")
        self.layout.addWidget(self.heading_label)

        # Add buttons
        self.student_login_button = QPushButton('Student Login', self)
        self.student_login_button.setStyleSheet(self.button_style())
        self.student_login_button.clicked.connect(self.open_student)
        
        self.admin_login_button = QPushButton('Admin Login', self)
        self.admin_login_button.setStyleSheet(self.button_style())
        self.admin_login_button.clicked.connect(self.open_admin)
        
        self.login_camera_button = QPushButton('Login Camera', self)
        self.login_camera_button.setStyleSheet(self.button_style())
        self.login_camera_button.clicked.connect(self.open_login_camera)
        
        self.logout_camera_button = QPushButton('Logout Camera', self)
        self.logout_camera_button.setStyleSheet(self.button_style())
        self.logout_camera_button.clicked.connect(self.open_logout_camera)

        self.layout.addWidget(self.student_login_button)
        self.layout.addWidget(self.admin_login_button)
        self.layout.addWidget(self.login_camera_button)
        self.layout.addWidget(self.logout_camera_button)
        
        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.student_login_button)
        hbox1.addWidget(self.admin_login_button)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.login_camera_button)
        hbox2.addWidget(self.logout_camera_button)

        # Add horizontal layouts to the vertical layout
        self.layout.addStretch(1)
        self.layout.addLayout(hbox1)
        self.layout.addLayout(hbox2)
        self.layout.addStretch(1)

    def open_login_camera(self):
        self.login_video_window = VideoCapture("login")
        self.login_video_window.show()
    
    def open_logout_camera(self):
        self.logout_video_window = VideoCapture("logout")
        self.logout_video_window.show()

    def open_student(self):
        self.student_window = student()
        self.student_window.show()
        
    def open_admin(self):
        self.admin_window=admin_login()
        self.admin_window.show()
       

# STUDENT HOME PAGE ,LOGIN WITH FACE RECOGNITION AND OPEN THE ATTENDENCE LIST
class student(QMainWindow, StyleContainer):
    def __init__(self):
        super().__init__()

        self.name = ""
        self.usn = ""
        self.setWindowTitle('Student Window')
        self.setGeometry(100, 100, 1280, 720)

        # Create the stacked widget
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        self.stacked_widget.setStyleSheet("QWidget { " + self.window_style() + " }")

        # First widget setup
        self.first_widget = QWidget()
        self.first_layout = QVBoxLayout()
        self.first_widget.setLayout(self.first_layout)

        # Heading for first widget
        self.heading_label = QLabel('Student Login')
        self.heading_label.setAlignment(Qt.AlignCenter)
        self.heading_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 20px; margin-bottom: 20px;")
        self.first_layout.addWidget(self.heading_label)

        # Form layout for inputs
        self.form_layout = QFormLayout()

        # USN input field
        self.student_usn_label = QLabel('User USN:')
        self.student_usn_input = QLineEdit(self)
        self.student_usn_input.setStyleSheet("font-size: 14px; width: 50px;")  # Adjust width here
        self.form_layout.addRow(self.student_usn_label, self.student_usn_input)

        # Video display (assuming video_label needs to be updated with video frames)
        self.video_label = QLabel(self)
        self.form_layout.addRow(self.video_label)
        
        self.video_capture=VideoCapture("0")
        self.encodedListImages=self.video_capture.get_encoded_list()
        self.classNames=self.video_capture.get_classNames()

        # Start button aligned to the right
        self.start_button = QPushButton('Start', self)
        self.start_button.setStyleSheet(self.button_style())
        self.start_button.clicked.connect(self.start_video)
        self.start_button.setMaximumWidth(150)  # Limit button width
        self.form_layout.addRow('', self.start_button)  # Empty label for alignment

        # Submit button aligned to the right
        self.submit_button = QPushButton('Submit', self)
        self.submit_button.setStyleSheet(self.button_style())
        self.submit_button.clicked.connect(self.s_submit)
        self.submit_button.setMaximumWidth(150)  # Limit button width
        
        # Horizontal layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.submit_button)
        button_layout.addStretch()  # Optional: add stretch to push buttons to the sides

        self.form_layout.addRow('', self.submit_button)  # Empty label for alignment

        # Add form layout to first widget layout
        self.first_layout.addLayout(self.form_layout)

        # Initialize timer and video capture
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_frame)
        self.cap = None  # Assuming you'll initialize this later in your start_video method

        # Second widget setup (for the table display, not shown here)
        self.second_widget = QWidget()
        self.second_layout = QVBoxLayout()
        self.second_widget.setLayout(self.second_layout)
        self.second_widget.setStyleSheet("QWidget { " + self.window_style() + " }")
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(6)  # Adjust column count based on your data
        self.table_widget.setHorizontalHeaderLabels(['USN', 'Name', 'Date', 'Month', 'LoginTime', 'LogoutTime'])  # Column headers
        self.second_layout.addWidget(self.table_widget)

        # Add both widgets to the stacked widget
        self.stacked_widget.addWidget(self.first_widget)
        self.stacked_widget.addWidget(self.second_widget)


    def start_video(self):
        usn=self.student_usn_input.text()
        exist_usn=[]
        for s in self.classNames:
            exist_usn.append(s.split('_')[1])
       
        print(exist_usn)
        if usn in exist_usn:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(3, 1280)
            self.cap.set(4, 720)
            self.timer.start(20)
        else:
            QMessageBox.warning(self, 'INCORRECT', 'Please Check the USN correctly')
    
    def stop_video(self):
        self.timer.stop()
        if self.cap:
            self.cap.release()
        self.video_label.clear()

    def check_frame(self):
        success, img = self.cap.read()
        if not success:
            return

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        facesCurFrame = face_recognition.face_locations(img)
        encodedCurFrame = face_recognition.face_encodings(img, facesCurFrame)
        for encodeFace, faceloc in zip(encodedCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(self.encodedListImages, encodeFace)
            faceDis = face_recognition.face_distance(self.encodedListImages, encodeFace)
            matchIndex = np.argmin(faceDis)
            if matches[matchIndex]:
                name = self.classNames[matchIndex].upper()
                name,usn=name.split('_')
                self.name=name
                self.usn=usn
                y1, x2, y2, x1 = faceloc
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(img, name, (x1 + 8, y2 + 8), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 25, 25), 2)
                print(name)
            else:
                y1, x2, y2, x1 = faceloc
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(img, "UNKNOWN", (x1 + 8, y2 + 8), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 25, 25), 2)

        qimg = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qimg))
    
    def s_submit(self):
        usn=self.student_usn_input.text()

        print("hello")
        if self.cap:
            self.cap.release()

        if(usn.upper()!=self.usn):
             QMessageBox.warning(self, 'INCORRECT', 'Please Check the USN correctly')
        else:
            self.stacked_widget.setCurrentWidget(self.second_widget)
            try:
                conn=sqlite3.connect('student_details.db')
                c=conn.cursor()
                c.execute("SELECT * FROM attendance WHERE name=?",(self.name,))
                rows=c.fetchall()
           
                self.table_widget.setColumnCount(len(rows[0]))
                self.table_widget.setRowCount(len(rows))
            
                for r,r_data in enumerate(rows):
                    for c,c_data in enumerate(r_data):
                        self.table_widget.setItem(r,c,QTableWidgetItem(str(c_data)))
        
            except sqlite3 as e:
                print(f"Database error :{e}")
            finally:
                conn.close()
                
class VideoCapture(QMainWindow, StyleContainer):
    def __init__(self,Check):
        super().__init__()
        self.check=Check
        print(self.check)
        self.setWindowTitle('Face Recognition')
        self.setGeometry(100, 100, 1280, 720)
        
        # Load images and create encodings
        self.path = r"C:\Stuff\Documents\College\Mini projects\Facial recognition\images"
        self.images = []
        self.classNames = []
        self.load_images()

        # Set up the main window
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.central_widget.setStyleSheet("QWidget { " + self.window_style() + " }")
        
        self.heading_label = QLabel('Video Capture for Facial Recognition')
        self.heading_label.setAlignment(Qt.AlignCenter)
        self.heading_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 20px; margin-bottom: 20px;")
        self.layout.addWidget(self.heading_label)

        # Add a QLabel to display the video
        self.video_label = QLabel(self)
        self.layout.addWidget(self.video_label)

        # Add a button to start the video
        self.start_button = QPushButton('Start', self)
        self.start_button.setStyleSheet(self.button_style())
        self.start_button.clicked.connect(self.start_video)
        self.layout.addWidget(self.start_button)

        # Add a button to stop the video
        self.stop_button = QPushButton('close', self)
        self.stop_button.setStyleSheet(self.button_style())
        self.stop_button.clicked.connect(self.close_window)
        self.layout.addWidget(self.stop_button)

        # Timer to update the video
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.cap = None
        
    def load_images(self):
        mylist = os.listdir(self.path)
        for cl in mylist:
            curImg = cv2.imread(f'{self.path}/{cl}')
            self.images.append(curImg)
            self.classNames.append(os.path.splitext(cl)[0])
        self.encodedListImages = self.find_encodings(self.images)

    def find_encodings(self, images):
        encodedList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodedList.append(encode)
        return encodedList

    def get_encoded_list(self):
        return self.encodedListImages
    
    def get_classNames(self):
        return self.classNames
    
    def start_video(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)
        self.timer.start(20)

    def close_window(self):
        self.timer.stop()
        if self.cap:
            self.cap.release()
        self.video_label.clear()
        self.close()

    def update_frame(self):
        success, img = self.cap.read()
        if not success:
            return

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        facesCurFrame = face_recognition.face_locations(img)
        encodedCurFrame = face_recognition.face_encodings(img, facesCurFrame)

        for encodeFace, faceloc in zip(encodedCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(self.encodedListImages, encodeFace)
            faceDis = face_recognition.face_distance(self.encodedListImages, encodeFace)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                name = self.classNames[matchIndex].upper()
                name,usn=name.split('_')
                y1, x2, y2, x1 = faceloc
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(img, name+" "+usn, (x1 + 8, y2 + 8), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 25, 25), 2)
                now = datetime.now()
                self.current_time = now.strftime("%H:%M:%S")
                self.current_date = now.strftime("%d")
                self.current_month = now.strftime("%m")
                print(usn)
                try:
                    conn = sqlite3.connect('student_details.db')
                    c = conn.cursor()
                    c.execute("SELECT * FROM attendance WHERE name=? AND date=?", (name, self.current_date))
                    row = c.fetchall()
                    if self.check=='login':
                        if row:
                            print("already presented")
                            cv2.putText(img,"ALREADY PRESENTED", (x1 + 20, y2 + 100), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 25, 25), 2)
                        else:
                            cv2.putText(img,"ATTENDENCE COMPLETED", (x1 + 20, y2 + 100), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 25, 25), 2)
                            c.execute('''
                            INSERT INTO attendance (usn,name,date,month,login_time,logout_time)
                            VALUES (?,?,?,?,?,?)
                            ''', (usn,name, self.current_date, self.current_month,self.current_time,"0"))

                    elif self.check=='logout':
                        if not row:
                            QMessageBox.warning(self, 'INCORRECT', 'Please go to login button')

                        elif row and row[0][5]=="0":
                            c.execute('''UPDATE attendance set logout_time=? where name=? AND date=?''',(self.current_time,name,self.current_date))
                            cv2.putText(img,"LOGOUT ATTENDENCE COMPLETED", (x1 + 20, y2 + 100), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 25, 25), 2)
                        elif row and row[0][5]!="0":
                            cv2.putText(img,"LOGOUT ATTENDENCE ALREADY COMPLETED", (x1 + 20, y2 + 100), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 25, 25), 2)

                    conn.commit()
                except sqlite3.Error as e:
                    print(f"Database error: {e}")
                finally:
                    conn.close()

            else:
                y1, x2, y2, x1 = faceloc
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(img, "UNKNOWN", (x1 + 8, y2 + 8), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 25, 25), 2)

        qimg = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qimg))
                
# student attendence table list search by admin using date,name 
class Table_list(QMainWindow, StyleContainer):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Student Attendance Window')
        self.setGeometry(100, 100, 800, 500)
        
        # Create the main layout
        self.layout = QVBoxLayout()
        
        # Set central widget
        central_widget = QWidget()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)
        
        self.heading_label = QLabel('Student Attendance')
        self.heading_label.setAlignment(Qt.AlignCenter)
        self.heading_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 20px; margin-bottom: 20px;")
        self.layout.addWidget(self.heading_label)

        self.form_layout = QFormLayout()
    
        # USER Name input
        self.username_label = QLabel('User Name:')
        self.username_input = QLineEdit(self)
        self.form_layout.addRow(self.username_label, self.username_input)

        # DATE input
        self.date_label = QLabel('Enter date')
        self.date_input = QLineEdit(self)
        self.form_layout.addRow(self.date_label,self.date_input)

        #SUBMIT BUTTON
        self.submit_button = QPushButton('Submit', self)
        self.submit_button.setStyleSheet(self.button_style())
        self.submit_button.clicked.connect(self.list)
        self.form_layout.addRow(self.submit_button)

        self.layout.addLayout(self.form_layout)
        
        # Create a table widget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(6)  # Adjust column count based on your data
        self.table_widget.setHorizontalHeaderLabels(['USN','Name', 'Date','MONTH' ,'LoginTime','LogoutTime'])  # Column headers
        self.layout.addWidget(self.table_widget)
        self.list()

    def list(self):
        name = self.username_input.text()
        date = self.date_input.text()
        name=name.upper()
        try:
            conn=sqlite3.connect('student_details.db')
            c=conn.cursor()
            if(name=='' and date==''):
                c.execute('select * from attendance')
                rows=c.fetchall()
            elif(name!='' and date==''):
                c.execute('select * from attendance where name=?',(name,))
                rows=c.fetchall()
            elif(name=='' and date!=''):
                c.execute('select * from attendance where date=?',(date,))
                rows=c.fetchall()
            else:
                c.execute('select * from attendance where name=? and date=?',(name,date))
                rows=c.fetchall()
            if(len(rows)>0):
                self.table_widget.setColumnCount(len(rows[0]))
                self.table_widget.setRowCount(len(rows))
                for r,r_data in enumerate(rows):
                    for c,c_data in enumerate(r_data):
                        self.table_widget.setItem(r,c,QTableWidgetItem(str(c_data)))
            elif(len(rows)==0):
                QMessageBox.warning(self, 'TRY AGAIN', 'Please Check the name and date correctly')

        except sqlite3 as e:
            print(f"Database error :{e}")
        finally:
            conn.close()
       
if __name__ == '__main__':
    init_db()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
