"""
Icon-Manager für die gesamte Anwendung.
Lädt und cached SVG-Icons für konsistente Verwendung.
"""

from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtGui import QPainter, QImage
from PySide6.QtCore import Qt
import os

class IconManager:
    """Zentraler Manager für alle Icons in der Anwendung."""
    
    _instance = None
    _icons_cache = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(IconManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        
        # Basis-Pfad für Icons ermitteln
        # Von src/oberflaeche/... aus gesehen
        current_file = os.path.abspath(__file__)
        src_dir = os.path.dirname(os.path.dirname(current_file))
        self.icons_dir = os.path.join(os.path.dirname(src_dir), "icons")
        
        # Verfügbare Icons
        self.icon_files = {
            'werkzeugkasten': 'werkzeugkasten.svg',
            'ruestwerkzeug': 'ruestwerkzeug.svg',
            'admin': 'admin.svg',
            'suche': 'suche.svg',
            'maschine': 'maschine.svg',
        }
    
    def get_pixmap(self, icon_name: str, size: int = 64) -> QPixmap:
        """
        Lädt ein Icon als QPixmap in der gewünschten Größe.
        
        Args:
            icon_name: Name des Icons (z.B. 'werkzeugkasten')
            size: Größe in Pixeln (quadratisch)
            
        Returns:
            QPixmap des Icons oder leeres Pixmap bei Fehler
        """
        cache_key = f"{icon_name}_{size}"
        
        # Aus Cache laden wenn vorhanden
        if cache_key in self._icons_cache:
            return self._icons_cache[cache_key]
        
        # Icon-Datei ermitteln
        if icon_name not in self.icon_files:
            return QPixmap()
        
        icon_path = os.path.join(self.icons_dir, self.icon_files[icon_name])
        
        # SVG laden und rendern
        if not os.path.exists(icon_path):
            return QPixmap()
        
        renderer = QSvgRenderer(icon_path)
        image = QImage(size, size, QImage.Format_ARGB32)
        image.fill(0x00000000)  # Transparent
        
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        renderer.render(painter)
        painter.end()
        
        pixmap = QPixmap.fromImage(image)
        
        # Im Cache speichern
        self._icons_cache[cache_key] = pixmap
        
        return pixmap
    
    def get_icon(self, icon_name: str, size: int = 64) -> QIcon:
        """
        Lädt ein Icon als QIcon.
        
        Args:
            icon_name: Name des Icons
            size: Größe in Pixeln
            
        Returns:
            QIcon des Icons
        """
        pixmap = self.get_pixmap(icon_name, size)
        return QIcon(pixmap)
    
    def clear_cache(self):
        """Leert den Icon-Cache."""
        self._icons_cache.clear()


# Singleton-Instanz für einfachen Zugriff
icon_manager = IconManager()
