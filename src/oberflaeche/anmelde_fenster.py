from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                               QPushButton, QMessageBox)
from PySide6.QtCore import Qt

class LoginWindow(QDialog):
    def __init__(self, auth_manager, parent=None):
        super().__init__(parent)
        self.auth_manager = auth_manager
        self.setWindowTitle("Login - Werkzeugverwaltung")
        self.setFixedSize(300, 200)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        title_label = QLabel("Willkommen")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Benutzername")
        layout.addWidget(self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Passwort")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        
        login_btn = QPushButton("Anmelden")
        login_btn.clicked.connect(self.handle_login)
        layout.addWidget(login_btn)
        
        self.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if self.auth_manager.login(username, password):
            self.accept()
        else:
            QMessageBox.warning(self, "Fehler", "Ungültige Anmeldedaten")
