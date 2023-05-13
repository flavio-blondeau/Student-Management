import sys
import sqlite3
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QGridLayout, \
    QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, \
    QDialog, QVBoxLayout, QComboBox
from PyQt6.QtGui import QAction


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")

        # Menu creation
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")

        # Add student sub-menu item
        add_student_action = QAction("Add Student", self)
        # noinspection PyUnresolvedReferences
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        # Add student sub-menu item
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)

        # Table creation
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("ID", "Name", "Course", "Phone"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

    def load_data(self):
        """Populate table with data from database"""
        connection = sqlite3.connect("database.db")
        result = list(connection.execute("SELECT * FROM students"))
        self.table.setRowCount(0)
        for row_nr, row_data in enumerate(result):
            self.table.insertRow(row_nr)
            for col_nr, data in enumerate(row_data):
                self.table.setItem(row_nr, col_nr, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        """Create a dialog window for typing students data"""
        dialog = InsertDialog()
        dialog.exec()


class InsertDialog(QDialog):
    # noinspection PyUnresolvedReferences
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add course selection list widget
        self.course_name = QComboBox()
        courses = sorted(["Biology", "Math", "Physics", "Chemistry",
                          "English", "Art", "Astronomy", "History"])
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # Add phone widget
        self.phone = QLineEdit()
        self.phone.setPlaceholderText("Mobile phone number")
        layout.addWidget(self.phone)

        # Add submit button
        button = QPushButton("Register")
        button.clicked.connect(self.add_student)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        phone = self.phone.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, phone) VALUES (?, ?, ?)",
                       (name, course, phone))
        connection.commit()
        cursor.close()
        connection.close()
        student_management.load_data()


app = QApplication(sys.argv)
student_management = MainWindow()
student_management.show()
student_management.load_data()
sys.exit(app.exec())
