from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRectF, QPropertyAnimation, Property, QEasingCurve, QSize
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QLinearGradient, QFont

class CabinetVisualization(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(400)
        self.active_kasten = -1
        self.active_lade = -1
        self._open_factor = 0.0
        
        # Animation for drawer opening
        self._animation = QPropertyAnimation(self, b"open_factor", self)
        self._animation.setDuration(600)
        self._animation.setEasingCurve(QEasingCurve.OutBack)

    def get_open_factor(self):
        return self._open_factor

    def set_open_factor(self, value):
        self._open_factor = value
        self.update()

    open_factor = Property(float, get_open_factor, set_open_factor)

    def set_selection(self, kasten, lade):
        """
        Set the active drawer to visualize.
        kasten: int (1 or 2)
        lade: int (1-15)
        """
        if self.active_kasten == kasten and self.active_lade == lade:
            return

        self.active_kasten = kasten
        self.active_lade = lade
        
        # Reset and start animation
        self._animation.stop()
        self._animation.setStartValue(0.0)
        self._animation.setEndValue(1.0)
        self._animation.start()
        
    def clear_selection(self):
        self.active_kasten = -1
        self.active_lade = -1
        self._open_factor = 0.0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # Margins and spacing
        margin = 20
        spacing = 40
        
        avail_w = w - (2 * margin) - spacing
        avail_h = h - (2 * margin)
        
        # Calculate cabinet width to fit 2 side by side
        cab_w = avail_w / 2
        cab_h = avail_h
        
        # Draw Cabinet 1 (Left)
        self.draw_cabinet(painter, 1, margin, margin, cab_w, cab_h)
        
        # Draw Cabinet 2 (Right)
        self.draw_cabinet(painter, 2, margin + cab_w + spacing, margin, cab_w, cab_h)

    def draw_cabinet(self, painter, kasten_idx, x, y, w, h):
        # 3D Effect: Draw back panel shadow first (depth)
        depth = 8
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 80))
        painter.drawRoundedRect(x + depth, y + depth, w, h, 4, 4)
        
        # Housing (Dark Grey) with gradient for 3D effect
        housing_grad = QLinearGradient(x, y, x + w, y)
        housing_grad.setColorAt(0, QColor("#2a2a2a"))
        housing_grad.setColorAt(0.1, QColor("#3d3d3d"))
        housing_grad.setColorAt(0.5, QColor("#484848"))
        housing_grad.setColorAt(0.9, QColor("#3d3d3d"))
        housing_grad.setColorAt(1, QColor("#2a2a2a"))
        painter.setBrush(housing_grad)
        painter.drawRoundedRect(x, y, w, h, 4, 4)
        
        # Side panels for depth effect
        painter.setBrush(QColor("#1a1a1a"))
        # Left side
        painter.drawRect(x - 2, y, 2, h)
        # Right side
        painter.drawRect(x + w, y, 2, h)
        
        # Header (Top part) with metallic gradient
        header_h = h * 0.05
        header_grad = QLinearGradient(x, y, x, y + header_h)
        header_grad.setColorAt(0, QColor("#404040"))
        header_grad.setColorAt(0.5, QColor("#2a2a2a"))
        header_grad.setColorAt(1, QColor("#1a1a1a"))
        painter.setBrush(header_grad)
        painter.drawRoundedRect(x, y, w, header_h, 4, 4)
        
        # Drawers area
        drawers_y = y + header_h + 5
        drawers_h = h - header_h - 10
        
        # Support up to 15 drawers
        num_drawers = 15 
        drawer_gap = 2
        single_drawer_h = (drawers_h - (num_drawers - 1) * drawer_gap) / num_drawers
        
        for i in range(num_drawers):
            lade_num = i + 1
            dy = drawers_y + i * (single_drawer_h + drawer_gap)
            
            is_active = (kasten_idx == self.active_kasten and lade_num == self.active_lade)
            
            # Drawer Rect
            dx = x + 5
            dw = w - 10
            
            # Animation: Slide out to the right
            offset = 0
            if is_active:
                offset = 50 * self._open_factor
            
            # Multi-layer shadow for depth (stronger 3D effect)
            if is_active:
                # Shadow layer 1 (darkest, furthest)
                painter.setBrush(QColor(0, 0, 0, 120))
                painter.drawRect(dx + 8, dy + 8, dw, single_drawer_h)
                # Shadow layer 2 (medium)
                painter.setBrush(QColor(0, 0, 0, 80))
                painter.drawRect(dx + 6, dy + 6, dw, single_drawer_h)
                # Shadow layer 3 (lightest, closest)
                painter.setBrush(QColor(0, 0, 0, 40))
                painter.drawRect(dx + 3, dy + 3, dw, single_drawer_h)
            
            # Drawer Color - Blue like image
            base_color = QColor("#005090")
            if is_active:
                base_color = QColor("#0078D7") 
            
            # Front face of drawer
            grad = QLinearGradient(dx + offset, dy, dx + offset, dy + single_drawer_h)
            grad.setColorAt(0, base_color.lighter(150))
            grad.setColorAt(0.2, base_color.lighter(120))
            grad.setColorAt(0.5, base_color)
            grad.setColorAt(0.8, base_color.darker(120))
            grad.setColorAt(1, base_color.darker(140))
            
            painter.setBrush(grad)
            painter.drawRoundedRect(dx + offset, dy, dw, single_drawer_h, 2, 2)
            
            # 3D edge highlights on front
            painter.setPen(QPen(base_color.lighter(180), 1))
            painter.drawLine(dx + offset, dy, dx + offset + dw, dy)
            
            painter.setPen(QPen(base_color.darker(150), 1))
            painter.drawLine(dx + offset, dy + single_drawer_h, 
                           dx + offset + dw, dy + single_drawer_h)
            
            painter.setPen(Qt.NoPen)
            
            # Handle (Silver strip) with enhanced chrome effect
            handle_h = single_drawer_h * 0.35
            handle_y = dy + (single_drawer_h - handle_h) / 2
            
            # Handle Gradient (Chrome/Metallic)
            handle_grad = QLinearGradient(dx + offset, handle_y, dx + offset, handle_y + handle_h)
            handle_grad.setColorAt(0, QColor("#c8c8c8"))
            handle_grad.setColorAt(0.3, QColor("#f5f5f5"))
            handle_grad.setColorAt(0.5, QColor("#ffffff"))
            handle_grad.setColorAt(0.7, QColor("#e8e8e8"))
            handle_grad.setColorAt(1, QColor("#a0a0a0"))
            
            painter.setBrush(handle_grad)
            painter.drawRect(dx + offset, handle_y, dw, handle_h)
            
            # Handle reflection highlight
            painter.setBrush(QColor(255, 255, 255, 100))
            painter.drawRect(dx + offset, handle_y, dw, handle_h * 0.3)
            
            # Label (Lade Number) - BLACK for better visibility
            font = painter.font()
            if is_active:
                font.setBold(True)
                font.setPointSize(14)
                painter.setPen(QColor("#000000"))  # Black
            else:
                font.setBold(False)
                font.setPointSize(8)
                painter.setPen(QColor("#000000"))  # Black
                
            painter.setFont(font)
            painter.drawText(QRectF(dx + offset, dy, dw, single_drawer_h), Qt.AlignCenter, str(lade_num))
