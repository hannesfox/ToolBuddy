from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                QPushButton, QGroupBox, QGridLayout, QScrollArea, QWidget)
from PySide6.QtCore import Qt
from ...modelle import Tool

class ToolDetailsDialog(QDialog):
    def __init__(self, tool: Tool, parent=None):
        super().__init__(parent)
        self.tool = tool
        self.setWindowTitle(f"Werkzeug Details - {tool.name}")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Scroll Area for all content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # === Basic Information ===
        basic_group = QGroupBox("Grundinformationen")
        basic_layout = QGridLayout()
        
        row = 0
        basic_layout.addWidget(QLabel("<b>WZ.Nr.:</b>"), row, 0)
        basic_layout.addWidget(QLabel(self.tool.id), row, 1)
        
        row += 1
        basic_layout.addWidget(QLabel("<b>Name:</b>"), row, 0)
        basic_layout.addWidget(QLabel(self.tool.name), row, 1)
        
        row += 1
        basic_layout.addWidget(QLabel("<b>Lagerplatz:</b>"), row, 0)
        basic_layout.addWidget(QLabel(self.tool.lagerplatz or "Nicht angegeben"), row, 1)
        
        row += 1
        basic_layout.addWidget(QLabel("<b>Hauptstatus:</b>"), row, 0)
        status_label = QLabel(self._format_status(self.tool.status))
        status_label.setStyleSheet(self._get_status_color(self.tool.status))
        basic_layout.addWidget(status_label, row, 1)

        # Rüstwerkzeug Location Check
        if self.tool.status in ['Rüstwerkzeuge', 'RÜSTWERKZEUG']:
            # We need to fetch the Ruestwerkzeug data. 
            # Since we don't have direct access to DataManager here (passed as parent maybe?), 
            # we should probably pass it or fetch it.
            # Looking at DetailedSearchPage, it passes `self` as parent.
            # DetailedSearchPage has `self.data_manager`.
            
            ruest_location = "Nicht gefunden"
            if hasattr(self.parent(), 'data_manager'):
                dm = self.parent().data_manager
                ruest_tools = dm.load_ruestwerkzeuge()
                # Find by ID
                for rt in ruest_tools:
                    if rt.id == self.tool.id:
                        ruest_location = f"Kasten {rt.kasten} / Lade {rt.lade} / Fach {rt.fach} (Bestand: {rt.bestand})"
                        break
            
            row += 1
            basic_layout.addWidget(QLabel("<b>Rüst-Lagerort:</b>"), row, 0)
            loc_label = QLabel(ruest_location)
            loc_label.setStyleSheet("color: #E50914; font-weight: bold;")
            basic_layout.addWidget(loc_label, row, 1)
        
        basic_group.setLayout(basic_layout)
        scroll_layout.addWidget(basic_group)
        
        # === Machine Assignment ===
        machine_group = QGroupBox("Maschinenzuordnung")
        machine_layout = QVBoxLayout()
        
        has_machine = False
        for i in range(1, 5):
            machine_key = f'Maschine_Box_{i}'
            status_key = f'Status_Box_{i}'
            
            if machine_key in self.tool.extra_data and self.tool.extra_data[machine_key]:
                has_machine = True
                machine_name = self.tool.extra_data[machine_key]
                box_status = self.tool.extra_data.get(status_key, 'unbekannt')
                
                machine_info = QHBoxLayout()
                machine_info.addWidget(QLabel(f"<b>Werkzeugkasten {i}:</b>"))
                machine_info.addWidget(QLabel(f"🔧 {machine_name}"))
                machine_info.addWidget(QLabel(f"({self._format_status(box_status)})"))
                machine_info.addStretch()
                
                machine_layout.addLayout(machine_info)
        
        if not has_machine:
            machine_layout.addWidget(QLabel("Keine Maschinenzuordnung vorhanden"))
        
        machine_group.setLayout(machine_layout)
        scroll_layout.addWidget(machine_group)
        
        # === Additional Data ===
        if self.tool.extra_data:
            extra_group = QGroupBox("Zusätzliche Informationen")
            extra_layout = QGridLayout()
            
            row = 0
            # Filter out the status and machine keys we already displayed
            excluded_keys = {f'Status_Box_{i}' for i in range(1, 5)}
            excluded_keys.update({f'Maschine_Box_{i}' for i in range(1, 5)})
            
            for key, value in sorted(self.tool.extra_data.items()):
                if key not in excluded_keys and value:  # Only show non-empty values
                    extra_layout.addWidget(QLabel(f"<b>{key}:</b>"), row, 0)
                    extra_layout.addWidget(QLabel(str(value)), row, 1)
                    row += 1
            
            if row == 0:
                extra_layout.addWidget(QLabel("Keine zusätzlichen Informationen"), 0, 0)
            
            extra_group.setLayout(extra_layout)
            scroll_layout.addWidget(extra_group)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # === Close Button ===
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Schließen")
        close_btn.clicked.connect(self.accept)
        close_btn.setMinimumWidth(120)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def _format_status(self, status: str) -> str:
        """Format status for display"""
        status_map = {
            'maschine': 'MASCHIENE',
            'gerüstet': 'GERÜSTET',
            'Rüstwerkzeuge': 'RÜSTWERKZEUG',
            'frei': 'FREI'
        }
        return status_map.get(status, status.upper())
    
    def _get_status_color(self, status: str) -> str:
        """Get color styling for status"""
        if status in ['maschine', 'MASCHIENE']:
            return "color: #00C7FC; font-weight: bold;"  # COLOR-3
        elif status in ['gerüstet', 'GERÜSTET']:
            return "color: #00CBF6; font-weight: bold;"  # COLOR-2
        elif status in ['Rüstwerkzeuge', 'RÜSTWERKZEUG']:
            return "color: #58ACFF; font-weight: bold;"  # COLOR-4
        elif status == 'frei':
            return "color: #00BAC4; font-weight: bold;"  # COLOR-1
        else:
            return "color: #ffffff;"
