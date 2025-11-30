from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QLabel,
                               QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QHBoxLayout)
from PySide6.QtCore import Qt
from ...daten_manager import DataManager
from ..dialoge.werkzeug_details_dialog import ToolDetailsDialog

class DetailedSearchPage(QWidget):
    def __init__(self, data_manager: DataManager):
        super().__init__()
        self.data_manager = data_manager
        self.tools = []
        
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("Suche")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1ABC9C; margin-bottom: 10px;")
        layout.addWidget(header)

        # Search Controls
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Suche...")
        self.search_input.setMinimumHeight(60)
        self.search_input.setStyleSheet("font-size: 18px; padding: 10px;")
        self.search_input.textChanged.connect(self.filter_tools)
        search_layout.addWidget(self.search_input)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Alle Status", "MASCHIENE", "GERÜSTET", "RÜSTWERKZEUG"])
        self.status_filter.setMinimumHeight(60)
        self.status_filter.setStyleSheet("font-size: 18px; padding: 10px;")
        self.status_filter.currentIndexChanged.connect(self.filter_tools)
        search_layout.addWidget(self.status_filter)
        
        layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setStyleSheet("QTableWidget::item { font-size: 16px; min-height: 50px; }")
        self.table.verticalHeader().setDefaultSectionSize(60)
        self.table.verticalHeader().hide()
        self.table.setShowGrid(True)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.show_tool_details)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        
    def refresh_data(self):
        self.tools = self.data_manager.load_tools()
        self.update_table(self.tools)
        
    def update_table(self, tools):
        headers = self.data_manager.fieldnames
        if not headers:
            headers = ["WZ.Nr.", "Name", "Status", "Pos."] # Fallback
            
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        
        # Configure column widths
        for i, header in enumerate(headers):
            if header == "Name":
                self.table.setColumnWidth(i, 300)  # Name column wider
            elif header == "WZ.Nr.":
                self.table.setColumnWidth(i, 80)
            elif header == "Pos.":
                self.table.setColumnWidth(i, 80)
            elif header == "Status":
                self.table.setColumnWidth(i, 200)
            else:
                self.table.setColumnWidth(i, 120)  # Default for other columns
        
        self.table.setRowCount(0)
        for tool in tools:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Reconstruct full dict for display
            row_data = tool.extra_data.copy()
            row_data['WZ.Nr.'] = tool.id
            row_data['Name'] = tool.name
            row_data['Pos.'] = tool.lagerplatz
            
            # Check if tool is in any machine by checking Status_Box_X fields
            machine_name = None
            for i in range(1, 5):
                if tool.extra_data.get(f'Status_Box_{i}') == 'maschine':
                    machine_name = tool.extra_data.get(f'Maschine_Box_{i}', '')
                    if machine_name:
                        break
            
            # Map status back for display with machine name if applicable
            if machine_name:
                row_data['Status'] = f'MASCHIENE ({machine_name})'
            elif tool.status == 'maschine':
                row_data['Status'] = 'MASCHIENE'
            elif tool.status == 'gerüstet':
                row_data['Status'] = 'GERÜSTET'
            elif tool.status == 'Rüstwerkzeuge':
                row_data['Status'] = 'RÜSTWERKZEUG'
            else:
                row_data['Status'] = tool.status.upper() if tool.status else ''

            for col, header in enumerate(headers):
                val = row_data.get(header, "")
                item = QTableWidgetItem(str(val))
                self.table.setItem(row, col, item)
                
                # Store Name + Lagerplatz in first column for unique identification
                if col == 0:
                    item.setData(Qt.UserRole, {'name': tool.name, 'pos': tool.lagerplatz})


    def filter_tools(self):
        query = self.search_input.text().lower()
        status_filter = self.status_filter.currentText()
        
        filtered = []
        for t in self.tools:
            # Check Status Filter
            # Map internal status to display status for comparison
            display_status = t.status
            if t.status == 'maschine': display_status = 'MASCHIENE'
            elif t.status == 'gerüstet': display_status = 'GERÜSTET'
            elif t.status == 'Rüstwerkzeuge': display_status = 'RÜSTWERKZEUG'
            
            if status_filter != "Alle Status" and display_status.upper() != status_filter:
                continue
            
            # Check Text Query
            match = False
            if query in t.name.lower() or query in t.id.lower(): match = True
            for val in t.extra_data.values():
                if query in str(val).lower():
                    match = True
                    break
            
            if match:
                filtered.append(t)
        self.update_table(filtered)
    
    def show_tool_details(self):
        """Show detailed information dialog for the selected tool"""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return
        
        # Get the tool data from the first column (Name + Lagerplatz)
        first_col_item = self.table.item(selected_row, 0)
        if not first_col_item:
            return
        
        tool_data = first_col_item.data(Qt.UserRole)
        if not tool_data:
            return
        
        # Find the tool by Name + Lagerplatz (ID is only for external programs)
        tool = None
        for t in self.tools:
            if t.name == tool_data['name'] and t.lagerplatz == tool_data['pos']:
                tool = t
                break
        
        if tool:
            dialog = ToolDetailsDialog(tool, self)
            dialog.exec()
