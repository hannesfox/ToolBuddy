
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLabel, QFrame
)
from PySide6.QtCore import Qt, QTimer, QDateTime

class Toolbar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Toolbar")
        self.setFixedHeight(50)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)
        
        layout.addStretch()
        
        # Right Side Info
        self.lbl_time = QLabel()
        self.lbl_time.setStyleSheet("color: #BDC3C7; font-weight: bold;")
        layout.addWidget(self.lbl_time)
        
        # Timer for clock
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()
        
    def update_time(self):
        now = QDateTime.currentDateTime()
        self.lbl_time.setText(now.toString("dd.MM.yyyy HH:mm"))
