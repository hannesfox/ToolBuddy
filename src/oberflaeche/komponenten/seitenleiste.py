
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTreeWidget, QTreeWidgetItem, QFrame, QStyle, QLineEdit, QDialog, QFormLayout, QComboBox
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QFont
from ..icon_manager import icon_manager

class LoginDialog(QDialog):
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Benutzer wechseln")
        self.setModal(True)
        self.setFixedSize(350, 180)
        
        layout = QFormLayout(self)
        
        # Load users and populate dropdown
        self.user_combo = QComboBox()
        self.user_combo.setMinimumHeight(35)
        users = data_manager.load_users()
        
        for user in users:
            username = user.get('Username', '')
            role = user.get('Role', '')
            role_display = {
                'admin': 'Administrator',
                'lager': 'Lager',
                'user': 'Benutzer'
            }.get(role, role)
            
            # Display format: "Username (Role)"
            display_text = f"{username} ({role_display})"
            self.user_combo.addItem(display_text, username)  # Store actual username as data
        
        layout.addRow("Benutzer:", self.user_combo)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Passwort (falls erforderlich)")
        self.password_input.setMinimumHeight(35)
        layout.addRow("Passwort:", self.password_input)
        
        btn_layout = QHBoxLayout()
        self.btn_ok = QPushButton("Anmelden")
        self.btn_ok.setMinimumHeight(35)
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel = QPushButton("Abbrechen")
        self.btn_cancel.setMinimumHeight(35)
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)
        layout.addRow(btn_layout)
    
    def get_credentials(self):
        # Get the actual username from the combo box item data
        username = self.user_combo.currentData()
        password = self.password_input.text()
        return username, password

class Sidebar(QWidget):
    page_selected = Signal(str)
    login_changed = Signal()  # Signal to notify when login status changes

    def __init__(self, auth_manager, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(300)
        self.auth_manager = auth_manager
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # --- Header Area ---
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(15, 15, 15, 15)
        
        # "Navigation" Label
        lbl_nav = QLabel("Navigation")
        lbl_nav.setProperty("class", "section-header")
        lbl_nav.setStyleSheet("font-size: 16px; color: #BDC3C7; font-weight: bold;")
        
        header_layout.addWidget(lbl_nav)
        header_layout.addStretch()
        
        self.main_layout.addWidget(header_widget)
        
        # --- Navigation (Tree View) ---
        self.nav_tree = QTreeWidget()
        self.nav_tree.setHeaderHidden(True)
        self.nav_tree.setIndentation(20)
        self.nav_tree.setRootIsDecorated(True)
        self.nav_tree.setFocusPolicy(Qt.NoFocus)
        self.nav_tree.itemClicked.connect(self.on_item_clicked)
        
        self.main_layout.addWidget(self.nav_tree)
        self.main_layout.addStretch()
        
        # --- Login/User Area (at bottom) ---
        self.user_container = QFrame()
        self.user_container.setStyleSheet("""
            QFrame {
                background-color: #1A252F;
                border-top: 1px solid #5D6D7E;
                padding: 10px;
            }
        """)
        user_layout = QVBoxLayout(self.user_container)
        user_layout.setContentsMargins(15, 15, 15, 15)
        
        self.lbl_user = QLabel("Nicht angemeldet")
        self.lbl_user.setStyleSheet("font-size: 14px; font-weight: bold; color: #BDC3C7;")
        user_layout.addWidget(self.lbl_user)
        
        btn_user_layout = QHBoxLayout()
        self.btn_login = QPushButton("Login")
        self.btn_login.setStyleSheet("""
            QPushButton {
                background-color: #1ABC9C; 
                color: white; 
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #16A085;
            }
        """)
        self.btn_login.clicked.connect(self.show_login_dialog)
        
        self.btn_logout = QPushButton("Logout")
        self.btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C; 
                color: white; 
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        """)
        self.btn_logout.clicked.connect(self.logout)
        self.btn_logout.hide()
        
        btn_user_layout.addWidget(self.btn_login)
        btn_user_layout.addWidget(self.btn_logout)
        user_layout.addLayout(btn_user_layout)
        
        self.main_layout.addWidget(self.user_container)
        
        # Initialize navigation
        self.update_navigation()
        self.update_user_display()

    def update_navigation(self):
        """Update navigation items based on user role."""
        self.nav_tree.clear()
        
        # Base navigation items (always visible) - jetzt mit SVG-Icons
        base_items = [
            ("Dashboard", None),  # Dashboard hat kein spezielles Icon
            ("Werkzeugkasten", "werkzeugkasten"),
            ("Rüstwerkzeug", "ruestwerkzeug"),
            ("Suche", "suche"),
        ]
        
        for text, icon_name in base_items:
            item = QTreeWidgetItem(self.nav_tree)
            item.setText(0, text)
            
            # Verwende SVG-Icon wenn verfügbar
            if icon_name:
                icon = icon_manager.get_icon(icon_name, size=24)
                item.setIcon(0, icon)
            else:
                # Fallback zu Standard-Icon
                item.setIcon(0, self.style().standardIcon(QStyle.SP_DirHomeIcon))
            
            item.setData(0, Qt.UserRole, text)
        
        # Add Admin item if user is admin
        if self.auth_manager.is_admin():
            admin_item = QTreeWidgetItem(self.nav_tree)
            admin_item.setText(0, "Admin")
            admin_icon = icon_manager.get_icon("admin", size=24)
            admin_item.setIcon(0, admin_icon)
            admin_item.setData(0, Qt.UserRole, "Admin")

        
        self.nav_tree.expandAll()

    def update_user_display(self):
        """Update user display based on login status."""
        if self.auth_manager.current_user:
            username = self.auth_manager.current_user.username
            role = self.auth_manager.current_user.role
            role_display = {
                'admin': 'Administrator',
                'lager': 'Lager',
                'user': 'Benutzer'
            }.get(role, role)
            
            self.lbl_user.setText(f"{username}\n({role_display})")
            
            # Change login button to "Wechseln" (Switch account)
            self.btn_login.setText("Wechseln")
            self.btn_login.setStyleSheet("""
                QPushButton {
                    background-color: #3498DB; 
                    color: white; 
                    padding: 8px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980B9;
                }
            """)
            self.btn_login.show()
            self.btn_logout.show()
        else:
            self.lbl_user.setText("Nicht angemeldet")
            self.btn_login.setText("Login")
            self.btn_login.setStyleSheet("""
                QPushButton {
                    background-color: #1ABC9C; 
                    color: white; 
                    padding: 8px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #16A085;
                }
            """)
            self.btn_login.show()
            self.btn_logout.hide()

    def show_login_dialog(self):
        """Show login dialog and process login."""
        from PySide6.QtWidgets import QMessageBox
        
        dialog = LoginDialog(self.auth_manager.data_manager, self)
        if dialog.exec():
            username, password = dialog.get_credentials()
            
            # Debug: Check what credentials were entered
            print(f"Login attempt - Username: '{username}', Password length: {len(password)}")
            
            if not username:
                QMessageBox.warning(self, "Login Fehler", "Bitte geben Sie einen Benutzernamen ein!")
                return
            
            if self.auth_manager.login(username, password):
                print(f"Login successful for user: {username}")
                self.update_user_display()
                self.update_navigation()
                self.login_changed.emit()
                QMessageBox.information(self, "Erfolg", f"Willkommen {username}!")
            else:
                print(f"Login failed for user: {username}")
                QMessageBox.warning(self, "Login Fehler", 
                    "Ungültige Anmeldedaten!\n\n"
                    "Verfügbare Benutzer:\n"
                    "- admin (mit Passwort)\n"
                    "- Lager (mit Passwort)\n"
                    "- Bediener (ohne Passwort)")

    def logout(self):
        """Logout current user."""
        self.auth_manager.logout()
        # Log back in as default "Bediener" user
        self.auth_manager.login("Bediener", "")
        self.update_user_display()
        self.update_navigation()
        self.login_changed.emit()

    def on_item_clicked(self, item, column):
        page_name = item.data(0, Qt.UserRole)
        if page_name:
            self.page_selected.emit(page_name)
