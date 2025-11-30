
class ModernStyles:
    # Color Palette
    COLOR_BACKGROUND = "#2C3E50"
    COLOR_BACKGROUND_DARK = "#1A252F"
    COLOR_ACCENT = "#5D6D7E"
    COLOR_TEXT = "#BDC3C7"
    COLOR_HIGHLIGHT = "#1ABC9C"  # Cyan/Turquoise
    COLOR_DANGER = "#E74C3C"
    COLOR_SUCCESS = "#2ECC71"
    
    # Fonts
    FONT_FAMILY = "Segoe UI, Roboto, Helvetica, Arial, sans-serif"
    
    @staticmethod
    def get_stylesheet():
        return f"""
        /* Global Reset */
        * {{
            font-family: "{ModernStyles.FONT_FAMILY}";
            font-size: 14px;
            color: {ModernStyles.COLOR_TEXT};
            outline: none;
        }}
        
        /* Main Window & Backgrounds */
        QMainWindow, QWidget#MainContent {{
            background-color: {ModernStyles.COLOR_BACKGROUND};
        }}
        
        QWidget#Sidebar {{
            background-color: {ModernStyles.COLOR_BACKGROUND_DARK};
            border-right: 1px solid {ModernStyles.COLOR_ACCENT};
        }}
        
        QWidget#Toolbar {{
            background-color: {ModernStyles.COLOR_BACKGROUND_DARK};
            border-top: 1px solid {ModernStyles.COLOR_ACCENT};
        }}
        
        /* Buttons */
        QPushButton {{
            background-color: {ModernStyles.COLOR_ACCENT};
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            color: #FFFFFF;
        }}
        
        QPushButton:hover {{
            background-color: #6E7F90; /* Slightly lighter accent */
        }}
        
        QPushButton:pressed {{
            background-color: #4B5866; /* Slightly darker accent */
        }}
        
        /* Icon Buttons (Transparent) */
        QPushButton.icon-btn {{
            background-color: transparent;
            border-radius: 4px;
        }}
        
        QPushButton.icon-btn:hover {{
            background-color: rgba(255, 255, 255, 0.1);
        }}
        
        /* Tiles (Dashboard) */
        QFrame.tile {{
            background-color: {ModernStyles.COLOR_BACKGROUND_DARK};
            border: 1px solid {ModernStyles.COLOR_ACCENT};
            border-radius: 12px;
        }}
        
        QFrame.tile:hover {{
            background-color: #23303C; /* Slightly lighter dark */
            border: 1px solid {ModernStyles.COLOR_HIGHLIGHT};
        }}
        
        QLabel.tile-icon {{
            font-size: 64px; /* Placeholder for icon size if using text, otherwise handled by icon size */
            color: {ModernStyles.COLOR_TEXT};
        }}
        
        QLabel.tile-label {{
            font-size: 18px;
            font-weight: bold;
            color: {ModernStyles.COLOR_TEXT};
        }}
        
        /* Sidebar Navigation (Tree/List) & Tables */
        QTreeWidget, QListWidget, QTableWidget {{
            background-color: #2C3E50;
            border: 1px solid #5D6D7E;
            outline: none;
            gridline-color: #FFFFFF; /* White grid lines */
            alternate-background-color: #34495E; /* Lighter row color */
            selection-background-color: #1ABC9C;
        }}
        
        QTreeWidget::item, QListWidget::item, QTableWidget::item {{
            padding: 8px;
            border: none;
        }}
        
        QTreeWidget::item:hover, QListWidget::item:hover, QTableWidget::item:hover {{
            background-color: rgba(255, 255, 255, 0.1);
        }}
        
        QTreeWidget::item:selected, QListWidget::item:selected, QTableWidget::item:selected {{
            background-color: rgba(26, 188, 156, 0.4);
            color: #FFFFFF;
        }}

        QHeaderView::section {{
            background-color: {ModernStyles.COLOR_BACKGROUND_DARK};
            color: {ModernStyles.COLOR_TEXT};
            padding: 8px;
            border: none;
            border-bottom: 2px solid {ModernStyles.COLOR_ACCENT};
            font-weight: bold;
        }}
        
        QTableCornerButton::section {{
            background-color: {ModernStyles.COLOR_BACKGROUND_DARK};
            border: none;
        }}
        
        /* ToDo List */
        QCheckBox {{
            spacing: 8px;
            padding: 4px;
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {ModernStyles.COLOR_ACCENT};
            border-radius: 4px;
            background: transparent;
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {ModernStyles.COLOR_SUCCESS};
            border-color: {ModernStyles.COLOR_SUCCESS};
            image: url(:/icons/check.png); /* Placeholder */
        }}
        
        QCheckBox::indicator:unchecked:hover {{
            border-color: {ModernStyles.COLOR_HIGHLIGHT};
        }}
        
        /* Headers */
        QLabel.header-title {{
            font-size: 24px;
            font-weight: bold;
            color: {ModernStyles.COLOR_HIGHLIGHT};
            padding: 10px;
        }}
        
        QLabel.section-header {{
            font-size: 14px;
            font-weight: bold;
            color: {ModernStyles.COLOR_ACCENT};
            text-transform: uppercase;
            padding: 10px 10px 5px 10px;
        }}
        
        /* Scrollbars */
        QScrollBar:vertical {{
            border: none;
            background: {ModernStyles.COLOR_BACKGROUND_DARK};
            width: 10px;
            margin: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background: {ModernStyles.COLOR_ACCENT};
            min-height: 20px;
            border-radius: 5px;
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        """
