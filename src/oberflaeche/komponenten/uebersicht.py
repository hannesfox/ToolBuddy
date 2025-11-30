
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QFrame, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QFont, QCursor, QPixmap
from ..icon_manager import icon_manager

class DashboardTile(QFrame):
    clicked = Signal()

    def __init__(self, title, icon_name, parent=None):
        super().__init__(parent)
        self.setProperty("class", "tile")
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setFixedSize(220, 220)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)
        
        # Icon Label - Verwende Icon-Manager
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignCenter)
        
        # Icon vom Icon-Manager laden
        pixmap = icon_manager.get_pixmap(icon_name, size=80)
        if not pixmap.isNull():
            self.icon_label.setPixmap(pixmap)
        else:
            # Fallback
            self.icon_label.setText("?")
            self.icon_label.setStyleSheet("font-size: 80px; color: #E50914;")
        
        # Text Label
        self.text_label = QLabel(title)
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setProperty("class", "tile-label")
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        
        # Shadow effect for depth
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(Qt.black)
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

class Dashboard(QWidget):
    page_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MainContent")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Title
        title = QLabel("»ToolBuddy«")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 48px; 
            font-weight: 300; 
            color: #BDC3C7;
            letter-spacing: 2px;
        """)
        layout.addWidget(title)
        
        # Grid
        grid_container = QWidget()
        grid = QGridLayout(grid_container)
        grid.setSpacing(30)
        grid.setAlignment(Qt.AlignCenter)
        
        # Tiles Data - jetzt mit Icon-Namen statt Pfaden
        tiles_data = [
            ("Werkzeugkasten", "werkzeugkasten", 0, 0, "Werkzeugkasten"),
            ("Rüstwerkzeug", "ruestwerkzeug", 0, 1, "Rüstwerkzeug"),
            ("Admin", "admin", 1, 0, "Admin"),
            ("Suche", "suche", 1, 1, "Suche"),
        ]
        
        for text, icon_name, r, c, page_name in tiles_data:
            tile = DashboardTile(text, icon_name)
            # Use lambda with default arg to capture variable correctly in loop
            tile.clicked.connect(lambda p=page_name: self.page_selected.emit(p))
            grid.addWidget(tile, r, c)
            
        layout.addWidget(grid_container)
        layout.addStretch()
