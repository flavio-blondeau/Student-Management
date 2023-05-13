import sqlite3
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QLabel, QGridLayout, \
    QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, \
    QDialog, QVBoxLayout, QComboBox, QToolBar, QStatusBar, QMessageBox


class DatabaseConnection:
    """Auxiliary class to prevent problems if database name changes"""
    def __init__(self, database_file="database.db"):
        self.database_file = database_file

    def connect(self):
        connection = sqlite3.connect(self.database_file)
        return connection


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")

        # Menu creation
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        # Add student sub-menu item
        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        # Add help sub-menu item
        about_action = QAction("About", self)
        about_action.triggered.connect(self.about)
        help_menu_item.addAction(about_action)

        # Add edit sub-menu item
        search_action = QAction("Search", self)
        edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)

        # Table creation
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("ID", "Name", "Course", "Phone"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Create toolbar
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # Create status bar
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def load_data(self):
        """Populate table with data from database"""
        connection = DatabaseConnection().connect()
        result = list(connection.execute("SELECT * FROM students"))
        self.table.setRowCount(0)
        for row_nr, row_data in enumerate(result):
            self.table.insertRow(row_nr)
            for col_nr, data in enumerate(row_data):
                self.table.setItem(row_nr, col_nr, QTableWidgetItem(str(data)))
        connection.close()

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)
        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        # Remove old statusbar buttons before adding new ones
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    @staticmethod
    def insert():
        """Create a dialog window for typing students data"""
        dialog = InsertDialog()
        dialog.exec()

    @staticmethod
    def search():
        dialog = SearchDialog()
        dialog.exec()

    @staticmethod
    def edit():
        dialog = EditDialog()
        dialog.exec()

    @staticmethod
    def delete():
        dialog = DeleteDialog()
        dialog.exec()

    @staticmethod
    def about():
        dialog = AboutDialog()
        dialog.exec()


class InsertDialog(QDialog):
    # noinspection PyUnresolvedReferences
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Student Data")
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
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        phone = self.phone.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)",
                       (name, course, phone))
        connection.commit()
        cursor.close()
        connection.close()
        student_management.load_data()

        self.close()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        name = self.student_name.text()
        # connection = DatabaseConnection().connect()
        # cursor = connection.cursor()
        # result = cursor.execute("SELECT * FROM students WHERE name = ?", (name,))
        # rows = list(result)
        items = student_management.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            student_management.table.item(item.row(), 1).setSelected(True)
        # cursor.close()
        # connection.close()

        self.close()


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Extract info about student
        index = student_management.table.currentRow()
        self.student_id = student_management.table.item(index, 0).text()
        student_name = student_management.table.item(index, 1).text()
        student_course = student_management.table.item(index, 2).text()
        student_phone = student_management.table.item(index, 3).text()

        # Edit student name widget
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Edit course selection list widget
        self.course_name = QComboBox()
        courses = sorted(["Biology", "Math", "Physics", "Chemistry",
                          "English", "Art", "Astronomy", "History"])
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(student_course)
        layout.addWidget(self.course_name)

        # Edit phone widget
        self.phone = QLineEdit(student_phone)
        self.phone.setPlaceholderText("Mobile phone number")
        layout.addWidget(self.phone)

        # Add submit button
        button = QPushButton("Register")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?",
                       (self.student_name.text(),
                        self.course_name.itemText(self.course_name.currentIndex()),
                        self.phone.text(),
                        self.student_id))
        connection.commit()
        cursor.close()
        connection.close()

        # Refresh table
        student_management.load_data()

        self.close()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")

        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)

        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)

    def delete_student(self):
        # Get selected row student id
        index = student_management.table.currentRow()
        student_id = student_management.table.item(index, 0).text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE id = ?", (student_id,))
        connection.commit()
        cursor.close()
        connection.close()

        # Refresh table
        student_management.load_data()

        self.close()
        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record has been deleted successfully!")
        confirmation_widget.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        This App has been created to collect students data.
        Feel free to modify and use the app as you wish.
        """
        self.setText(content)


app = QApplication(sys.argv)
student_management = MainWindow()
student_management.show()
student_management.load_data()
sys.exit(app.exec())
