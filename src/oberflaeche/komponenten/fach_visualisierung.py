from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QLinearGradient

class FachVisualization(QWidget):
    """Compact compartment visualization widget for displaying drawer compartments"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(200)
        self.active_fach = -1
        self.max_faecher = 6
        self.grid_rows = 0
        self.grid_cols = 0
        
    def set_compartment(self, fach, max_faecher=6, rows=0, cols=0):
        """
        Set the active compartment to highlight.
        If rows and cols are provided (>0), a fixed grid is used.
        Otherwise, a dynamic grid based on max_faecher is calculated.
        """
        self.active_fach = fach
        self.max_faecher = max_faecher
        self.grid_rows = rows
        self.grid_cols = cols
        self.update()
        
    def clear(self):
        """Clear the visualization"""
        self.active_fach = -1
        self.update()
    
    def paintEvent(self, event):
        if self.active_fach < 0:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # Margins
        margin = 10
        comp_area_w = w - 2 * margin
        comp_area_h = h - 2 * margin
        
        # Determine Grid Layout
        if self.grid_rows > 0 and self.grid_cols > 0:
            rows = self.grid_rows
            cols = self.grid_cols
            total_cells = rows * cols
        else:
            # Dynamic fallback
            if self.max_faecher <= 3:
                cols = self.max_faecher
                rows = 1
            elif self.max_faecher <= 6:
                cols = 3
                rows = 2
            elif self.max_faecher <= 9:
                cols = 3
                rows = 3
            elif self.max_faecher <= 12:
                cols = 4
                rows = 3
            else:
                cols = 4
                rows = (self.max_faecher + 3) // 4
            total_cells = self.max_faecher
        
        comp_gap = 4
        
        single_comp_w = (comp_area_w - (cols - 1) * comp_gap) / cols
        single_comp_h = (comp_area_h - (rows - 1) * comp_gap) / rows
        
        # Draw compartments
        # If using fixed grid, we draw all cells up to rows*cols
        # If dynamic, we draw up to max_faecher
        
        limit = total_cells if (self.grid_rows > 0) else self.max_faecher
        
        for i in range(limit):
            # Calculate logical number (1-based)
            fach_num = i + 1
            
            # Calculate position (row, col)
            if self.grid_rows > 0:
                # Fixed Grid: Front-Left (1) -> Back-Right (Max)
                # Visual Layout:
                # Row 0 (Top)    : ... Max
                # ...
                # Row N (Bottom) : 1 ...
                #
                # We want 1 at Bottom-Left.
                # So we fill from Bottom-Left to Right, then Up.
                # Or Bottom-Left to Up, then Right?
                # "links vorne mit 1 begonnen und bis rechts hinten sich steigern"
                # Usually implies reading order, but starting at front-left.
                # Let's assume Row-Major from Bottom-Left.
                
                # Logical Index (0 to total-1)
                # Row index from bottom (0 is bottom, rows-1 is top)
                row_from_bottom = i // cols
                col_index = i % cols
                
                # Visual Row (0 is top)
                row = (rows - 1) - row_from_bottom
                col = col_index
                
            else:
                # Dynamic: Standard Top-Left to Bottom-Right
                row = i // cols
                col = i % cols
            
            comp_cx = margin + col * (single_comp_w + comp_gap)
            comp_cy = margin + row * (single_comp_h + comp_gap)
            
            is_active = (self.active_fach == fach_num)
            
            # Compartment background
            if is_active:
                # Highlighted active compartment
                comp_grad = QLinearGradient(comp_cx, comp_cy, comp_cx, comp_cy + single_comp_h)
                comp_grad.setColorAt(0, QColor(255, 120, 20))
                comp_grad.setColorAt(0.5, QColor(255, 80, 0))
                comp_grad.setColorAt(1, QColor(200, 50, 0))
                painter.setBrush(comp_grad)
                painter.setPen(QPen(QColor(255, 200, 0), 3))
            else:
                # Darker compartments
                comp_grad = QLinearGradient(comp_cx, comp_cy, comp_cx, comp_cy + single_comp_h)
                comp_grad.setColorAt(0, QColor(50, 60, 70))
                comp_grad.setColorAt(1, QColor(30, 35, 40))
                painter.setBrush(comp_grad)
                painter.setPen(QPen(QColor(90, 100, 110), 1))
            
            painter.drawRoundedRect(int(comp_cx), int(comp_cy), 
                                  int(single_comp_w), int(single_comp_h), 4, 4)
            
            # Compartment number
            painter.setPen(QColor("#FFFFFF"))
            font = painter.font()
            if is_active:
                font.setPointSize(20)
                font.setBold(True)
            else:
                font.setPointSize(12)
                font.setBold(False)
            painter.setFont(font)
            painter.drawText(QRectF(comp_cx, comp_cy, single_comp_w, single_comp_h), 
                           Qt.AlignCenter, str(fach_num))
        
        # Draw "Vorne" / "Hinten" labels if fixed grid to help orientation
        if self.grid_rows > 0:
            painter.setPen(QColor("#7F8C8D"))
            font = painter.font()
            font.setPointSize(10)
            font.setBold(True)
            painter.setFont(font)
            
            # "Vorne" (Front) label at the bottom
            painter.drawText(QRectF(0, h - margin + 2, w, margin), Qt.AlignCenter, "VORNE (GRIFF)")
            
            # "Hinten" (Back) label at the top
            # painter.drawText(QRectF(0, 0, w, margin), Qt.AlignCenter, "HINTEN")
        
        painter.setPen(Qt.NoPen)
