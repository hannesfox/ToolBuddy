from PySide6.QtWidgets import (QDialog, QVBoxLayout, QGridLayout, QLineEdit, 
                               QComboBox, QDialogButtonBox, QLabel, QScrollArea, QWidget)
from ..modelle import Tool

class ToolDialog(QDialog):
    def __init__(self, parent=None, tool: Tool = None, data_manager=None):
        super().__init__(parent)
        self.tool = tool
        self.data_manager = data_manager
        self.extra_inputs = {}
        self.setWindowTitle("Werkzeug bearbeiten" if tool else "Neues Werkzeug")
        self.setMinimumWidth(900)  # Wider for 3 columns
        self.setMinimumHeight(600)
        
        main_layout = QVBoxLayout()
        
        # Scroll area for all fields
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Grid layout for fields (3 columns)
        grid_layout = QGridLayout()
        grid_layout.setColumnStretch(1, 1)  # Column 1 (first value column)
        grid_layout.setColumnStretch(3, 1)  # Column 3 (second value column)
        grid_layout.setColumnStretch(5, 1)  # Column 5 (third value column)
        
        # Core fields
        self.id_input = QLineEdit()
        if tool:
            self.id_input.setText(tool.id)
            self.id_input.setReadOnly(True)
        
        self.name_input = QLineEdit()
        if tool:
            self.name_input.setText(tool.name)
            
        self.status_input = QComboBox()
        self.status_input.addItems(["gerüstet", "maschine", "Rüstwerkzeuge"])
        if tool:
            self.status_input.setCurrentText(tool.status)
            
        self.lagerplatz_input = QLineEdit()
        if tool:
            self.lagerplatz_input.setText(tool.lagerplatz)
        
        # Add core fields to grid (first row)
        row = 0
        grid_layout.addWidget(QLabel("<b>ID:</b>"), row, 0)
        grid_layout.addWidget(self.id_input, row, 1)
        grid_layout.addWidget(QLabel("<b>Name:</b>"), row, 2)
        grid_layout.addWidget(self.name_input, row, 3)
        grid_layout.addWidget(QLabel("<b>Status:</b>"), row, 4)
        grid_layout.addWidget(self.status_input, row, 5)
        
        row += 1
        grid_layout.addWidget(QLabel("<b>Lagerplatz:</b>"), row, 0)
        grid_layout.addWidget(self.lagerplatz_input, row, 1)
        
        # Dynamic Fields in 3 columns
        if self.data_manager:
            core_fields = ['WZ.Nr.', 'ID', 'Name', 'Status', 'Pos.', 'Lagerplatz']
            
            extra_fields = [f for f in self.data_manager.fieldnames if f not in core_fields]
            
            col = 0  # Track which column we're in (0, 2, 4)
            for field in extra_fields:
                line_edit = QLineEdit()
                if tool and field in tool.extra_data:
                    line_edit.setText(tool.extra_data[field])
                
                # Move to next row after 3 columns
                if col >= 6:
                    row += 1
                    col = 0
                
                grid_layout.addWidget(QLabel(f"<b>{field}:</b>"), row, col)
                grid_layout.addWidget(line_edit, row, col + 1)
                self.extra_inputs[field] = line_edit
                
                col += 2  # Move to next column (0->2, 2->4, 4->6)
        
        scroll_layout.addLayout(grid_layout)
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)
        
        # Dynamic hint based on status
        self.hint_label = QLabel("")
        self.hint_label.setWordWrap(True)
        self.hint_label.setStyleSheet("color: #888; font-style: italic; font-size: 12px;")
        main_layout.addWidget(self.hint_label)
        
        self.status_input.currentTextChanged.connect(self.update_hint)
        self.update_hint(self.status_input.currentText())
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)
        
        self.setLayout(main_layout)
        
    def update_hint(self, status):
        if status == "gerüstet":
            self.hint_label.setText("Kann in den virtuellen Werkzeugkasten geladen werden.")
        elif status == "maschine":
            self.hint_label.setText("Befindet sich in der Maschine. Nur Suche.")
        elif status == "Rüstwerkzeuge":
            self.hint_label.setText("Bitte Lagerplatz zuweisen.")


    def get_data(self):
        extra_data = {}
        if self.tool:
            extra_data = self.tool.extra_data.copy()
            
        for field, input_widget in self.extra_inputs.items():
            extra_data[field] = input_widget.text()
            
        return Tool(
            id=self.id_input.text(),
            name=self.name_input.text(),
            status=self.status_input.currentText(),
            lagerplatz=self.lagerplatz_input.text(),
            extra_data=extra_data
        )
