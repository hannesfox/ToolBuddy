from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
                               QPushButton, QLabel, QLineEdit, QComboBox, QMessageBox,
                               QGroupBox, QFormLayout)
from ..daten_manager import DataManager

class UserManagementDialog(QDialog):
    def __init__(self, daten_manager: DataManager, parent=None):
        super().__init__(parent)
        self.daten_manager = daten_manager
        self.setWindowTitle("Benutzerverwaltung")
        self.resize(500, 400)
        
        layout = QHBoxLayout()
        
        # Left: User List
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Vorhandene Benutzer:"))
        self.user_list = QListWidget()
        left_layout.addWidget(self.user_list)
        
        delete_btn = QPushButton("Benutzer löschen")
        delete_btn.setObjectName("dangerButton")
        delete_btn.clicked.connect(self.delete_user)
        left_layout.addWidget(delete_btn)
        
        layout.addLayout(left_layout)
        
        # Right: Add User
        right_group = QGroupBox("Neuen Benutzer anlegen")
        right_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.role_input = QComboBox()
        self.role_input.addItems(["user", "admin"])
        
        right_layout.addRow("Benutzername:", self.username_input)
        right_layout.addRow("Passwort:", self.password_input)
        right_layout.addRow("Rolle:", self.role_input)
        
        add_btn = QPushButton("Anlegen")
        add_btn.clicked.connect(self.add_user)
        right_layout.addRow(add_btn)
        
        right_group.setLayout(right_layout)
        layout.addWidget(right_group)
        
        self.setLayout(layout)
        self.refresh_list()

    def refresh_list(self):
        self.user_list.clear()
        users = self.daten_manager.load_users()
        for user in users:
            self.user_list.addItem(f"{user['Username']} ({user['Role']})")

    def add_user(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        role = self.role_input.currentText()
        
        if not username or not password:
            QMessageBox.warning(self, "Fehler", "Bitte Benutzername und Passwort eingeben.")
            return
            
        if self.daten_manager.add_user(username, password, role):
            QMessageBox.information(self, "Erfolg", f"Benutzer {username} angelegt.")
            self.username_input.clear()
            self.password_input.clear()
            self.refresh_list()
        else:
            QMessageBox.warning(self, "Fehler", "Benutzer existiert bereits.")

    def delete_user(self):
        row = self.user_list.currentRow()
        if row < 0:
            return
            
        item_text = self.user_list.item(row).text()
        username = item_text.split(" (")[0]
        
        if username == "admin":
            QMessageBox.warning(self, "Fehler", "Der Haupt-Admin kann nicht gelöscht werden.")
            return
            
        confirm = QMessageBox.question(self, "Löschen", f"Benutzer {username} wirklich löschen?", 
                                     QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.daten_manager.delete_user(username)
            self.refresh_list()
