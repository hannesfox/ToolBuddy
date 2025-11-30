from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QMessageBox, QTabWidget, QGridLayout, QFrame,
                               QDialog, QFormLayout, QSpinBox, QComboBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from ...daten_manager import DataManager
from ...modelle import Ruestwerkzeug
from ...authentifizierung import AuthManager
from ..dialoge.laden_konfig_dialog import DrawerConfigDialog

class RuestwerkzeugPage(QWidget):
    def __init__(self, data_manager: DataManager, auth_manager: AuthManager):
        super().__init__()
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        
        self.layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Rüstwerkzeug")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1ABC9C; margin-bottom: 10px;")
        self.layout.addWidget(header)
        
        # Search Bar (Top)
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Suche...")
        self.search_bar.setMinimumHeight(60)
        self.search_bar.setStyleSheet("font-size: 18px; padding: 10px;")
        self.search_bar.textChanged.connect(self.filter_tools)
        self.layout.addWidget(self.search_bar)
        
        # Tabs
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # User Tab
        self.user_tab = QWidget()
        self.setup_user_tab()
        self.tabs.addTab(self.user_tab, "🔍 Suche & Entnahme")
        
        # Admin Tab
        self.admin_tab = QWidget()
        self.setup_admin_tab()
        self.tabs.addTab(self.admin_tab, "🛠️ Verwaltung")
        
        # Initial load
        self.refresh_data()

    def setup_user_tab(self):
        layout = QHBoxLayout(self.user_tab)
        
        # Left: List
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        self.tool_list = QTableWidget()
        self.tool_list.setColumnCount(3)
        self.tool_list.setHorizontalHeaderLabels(["Name", "Bestand", "Ort"])
        self.tool_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tool_list.setSelectionBehavior(QTableWidget.SelectRows)
        self.tool_list.setStyleSheet("QTableWidget::item { font-size: 18px; min-height: 60px; }")
        self.tool_list.verticalHeader().setDefaultSectionSize(60)
        self.tool_list.verticalHeader().hide()
        self.tool_list.setShowGrid(True)
        self.tool_list.setAlternatingRowColors(True)
        self.tool_list.itemSelectionChanged.connect(self.on_tool_selected)
        left_layout.addWidget(self.tool_list)
        
        layout.addWidget(left_panel, 1)
        
        # Right: Visualization and Action
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Info Box
        self.info_box = QFrame()
        self.info_box.setStyleSheet("background-color: #2b2b2b; border-radius: 10px; padding: 10px;")
        info_layout = QVBoxLayout(self.info_box)
        
        self.selected_tool_label = QLabel("Kein Werkzeug ausgewählt")
        self.selected_tool_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        info_layout.addWidget(self.selected_tool_label)
        
        self.location_label = QLabel("")
        info_layout.addWidget(self.location_label)
        
        self.stock_label = QLabel("")
        info_layout.addWidget(self.stock_label)
        
        # Add Fach Visualization in info box
        from ..komponenten.fach_visualisierung import FachVisualization
        self.fach_visualisierung = FachVisualization()
        self.fach_visualisierung.setMinimumHeight(150)
        info_layout.addWidget(self.fach_visualisierung)
        
        right_layout.addWidget(self.info_box)
        
        # Visualization
        from ..komponenten.schrank_visualisierung import CabinetVisualization
        self.schrank_visualisierung = CabinetVisualization()
        right_layout.addWidget(self.schrank_visualisierung)
        
        # Action Buttons
        action_layout = QHBoxLayout()
        self.take_btn = QPushButton("Entnehmen")
        self.take_btn.setStyleSheet("background-color: #E50914; color: white; font-weight: bold; padding: 10px;")
        self.take_btn.clicked.connect(self.take_tool)
        self.take_btn.setEnabled(False)
        action_layout.addWidget(self.take_btn)
        
        self.return_btn = QPushButton("Zurückgeben")
        self.return_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 10px;")
        self.return_btn.clicked.connect(self.return_tool)
        self.return_btn.setEnabled(False)
        action_layout.addWidget(self.return_btn)
        
        right_layout.addLayout(action_layout)
        
        layout.addWidget(right_panel, 1)

    def setup_admin_tab(self):
        layout = QVBoxLayout(self.admin_tab)
        
        # Toolbar
        toolbar = QHBoxLayout()
        add_btn = QPushButton("➕ Neues Werkzeug")
        add_btn.clicked.connect(self.add_tool_dialog)
        toolbar.addWidget(add_btn)
        
        edit_btn = QPushButton("✏️ Bearbeiten")
        edit_btn.clicked.connect(self.edit_tool_dialog)
        toolbar.addWidget(edit_btn)
        
        del_btn = QPushButton("🗑️ Löschen")
        del_btn.clicked.connect(self.delete_tool)
        toolbar.addWidget(del_btn)
        
        config_btn = QPushButton("⚙️ Ladenkonfiguration")
        config_btn.clicked.connect(self.open_drawer_config)
        toolbar.addWidget(config_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Table
        self.admin_table = QTableWidget()
        self.admin_table.setColumnCount(7)
        self.admin_table.setHorizontalHeaderLabels(["ID", "Name", "Kasten", "Lade", "Fach", "Bestand", "Min"])
        self.admin_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.admin_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.admin_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.admin_table.doubleClicked.connect(self.edit_tool_dialog)
        self.admin_table.setShowGrid(True)
        self.admin_table.setAlternatingRowColors(True)
        layout.addWidget(self.admin_table)

    def refresh_data(self):
        self.all_tools = self.data_manager.load_ruestwerkzeuge()
        self.filter_tools()
        
        # Check admin permission (Admin OR Lager)
        can_manage = self.auth_manager.is_lager_admin()
        self.tabs.setTabEnabled(1, can_manage)
        if not can_manage and self.tabs.currentIndex() == 1:
            self.tabs.setCurrentIndex(0)

    def filter_tools(self):
        query = self.search_bar.text().lower()
        filtered = [t for t in self.all_tools if query in t.name.lower() or query in t.id.lower()]
        
        # Update User List
        self.tool_list.setRowCount(len(filtered))
        for i, tool in enumerate(filtered):
            self.tool_list.setItem(i, 0, QTableWidgetItem(tool.name))
            self.tool_list.setItem(i, 1, QTableWidgetItem(str(tool.bestand)))
            self.tool_list.setItem(i, 2, QTableWidgetItem(f"K{tool.kasten}/L{tool.lade}/F{tool.fach}"))
            self.tool_list.item(i, 0).setData(Qt.UserRole, tool)

        # Update Admin Table
        self.admin_table.setRowCount(len(filtered))
        for i, tool in enumerate(filtered):
            self.admin_table.setItem(i, 0, QTableWidgetItem(tool.id))
            self.admin_table.setItem(i, 1, QTableWidgetItem(tool.name))
            self.admin_table.setItem(i, 2, QTableWidgetItem(str(tool.kasten)))
            self.admin_table.setItem(i, 3, QTableWidgetItem(str(tool.lade)))
            self.admin_table.setItem(i, 4, QTableWidgetItem(str(tool.fach)))
            self.admin_table.setItem(i, 5, QTableWidgetItem(str(tool.bestand)))
            self.admin_table.setItem(i, 6, QTableWidgetItem(str(tool.min_bestand)))
            self.admin_table.item(i, 0).setData(Qt.UserRole, tool)

    def on_tool_selected(self):
        items = self.tool_list.selectedItems()
        if not items:
            self.selected_tool_label.setText("Kein Werkzeug ausgewählt")
            self.location_label.setText("")
            self.stock_label.setText("")
            self.schrank_visualisierung.clear_selection()
            self.fach_visualisierung.clear()
            self.take_btn.setEnabled(False)
            return
            
        tool = items[0].data(Qt.UserRole)
        self.selected_tool_label.setText(tool.name)
        self.location_label.setText(f"Ort: Kasten {tool.kasten}, Lade {tool.lade}, Fach {tool.fach}")
        self.stock_label.setText(f"Bestand: {tool.bestand} (Min: {tool.min_bestand})")
        
        # Update Visualization
        # Fetch grid size from configuration
        rows, cols = self.data_manager.get_drawer_grid(tool.kasten, tool.lade)
        
        # Calculate max fach based on grid
        max_fach = rows * cols
        
        # Update fach visualization in info box with grid config
        self.fach_visualisierung.set_compartment(tool.fach, max_fach, rows=rows, cols=cols)
        
        # Update cabinet visualization (without detail panel)
        self.schrank_visualisierung.set_selection(tool.kasten, tool.lade)
        
        self.take_btn.setEnabled(tool.bestand > 0)
        self.return_btn.setEnabled(True)

    def open_drawer_config(self):
        dialog = DrawerConfigDialog(self.data_manager, self)
        dialog.exec()

    def take_tool(self):
        items = self.tool_list.selectedItems()
        if not items:
            return
        
        tool = items[0].data(Qt.UserRole)
        if tool.bestand > 0:
            tool.bestand -= 1
            
            # Immediate UI Update
            self.stock_label.setText(f"Bestand: {tool.bestand} (Min: {tool.min_bestand})")
            
            # Update list item immediately
            current_row = self.tool_list.currentRow()
            if current_row >= 0:
                 self.tool_list.setItem(current_row, 1, QTableWidgetItem(str(tool.bestand)))
            
            try:
                self.data_manager.update_ruestwerkzeug(tool)
                self.refresh_data()
                
                # Restore selection
                self.restore_selection(tool.id)
                
                QMessageBox.information(self, "Erfolg", f"1x {tool.name} entnommen.")
            except ValueError as e:
                QMessageBox.warning(self, "Fehler", str(e))

    def return_tool(self):
        items = self.tool_list.selectedItems()
        if not items:
            return
        
        tool = items[0].data(Qt.UserRole)
        tool.bestand += 1
        
        # Immediate UI Update
        self.stock_label.setText(f"Bestand: {tool.bestand} (Min: {tool.min_bestand})")
        
        # Update list item immediately
        current_row = self.tool_list.currentRow()
        if current_row >= 0:
             self.tool_list.setItem(current_row, 1, QTableWidgetItem(str(tool.bestand)))
        
        try:
            self.data_manager.update_ruestwerkzeug(tool)
            self.refresh_data()
            
            # Restore selection
            self.restore_selection(tool.id)
            
            QMessageBox.information(self, "Erfolg", f"1x {tool.name} zurückgegeben.")
        except ValueError as e:
            QMessageBox.warning(self, "Fehler", str(e))

    def restore_selection(self, tool_id):
        for i in range(self.tool_list.rowCount()):
            item = self.tool_list.item(i, 0)
            if item.data(Qt.UserRole).id == tool_id:
                self.tool_list.selectRow(i)
                break

    def add_tool_dialog(self):
        dialog = ToolEditDialog(self, data_manager=self.data_manager)
        if dialog.exec():
            data = dialog.get_data()
            # Generate ID if empty or handle duplicates
            if not data['id']:
                QMessageBox.warning(self, "Fehler", "ID darf nicht leer sein.")
                return
                
            new_tool = Ruestwerkzeug(
                id=data['id'],
                name=data['name'],
                kasten=data['kasten'],
                lade=data['lade'],
                fach=data['fach'],
                bestand=data['bestand'],
                min_bestand=data['min_bestand']
            )
            
            try:
                if self.data_manager.add_ruestwerkzeug(new_tool):
                    self.refresh_data()
                else:
                    QMessageBox.warning(self, "Fehler", "ID existiert bereits.")
            except ValueError as e:
                QMessageBox.warning(self, "Fehler", str(e))

    def edit_tool_dialog(self):
        items = self.admin_table.selectedItems()
        if not items:
            return
            
        tool = items[0].data(Qt.UserRole)
        dialog = ToolEditDialog(self, tool, data_manager=self.data_manager)
        if dialog.exec():
            data = dialog.get_data()
            tool.name = data['name']
            tool.kasten = data['kasten']
            tool.lade = data['lade']
            tool.fach = data['fach']
            tool.bestand = data['bestand']
            tool.min_bestand = data['min_bestand']
            
            try:
                self.data_manager.update_ruestwerkzeug(tool)
                self.refresh_data()
            except ValueError as e:
                QMessageBox.warning(self, "Fehler", str(e))

    def delete_tool(self):
        items = self.admin_table.selectedItems()
        if not items:
            return
            
        tool = items[0].data(Qt.UserRole)
        if QMessageBox.question(self, "Löschen", f"Soll {tool.name} wirklich gelöscht werden?") == QMessageBox.Yes:
            self.data_manager.delete_ruestwerkzeug(tool.id)
            self.refresh_data()

class ToolEditDialog(QDialog):
    def __init__(self, parent=None, tool: Ruestwerkzeug = None, data_manager=None):
        super().__init__(parent)
        self.setWindowTitle("Werkzeug bearbeiten" if tool else "Neues Werkzeug")
        self.setMinimumSize(600, 650)
        self.data_manager = data_manager
        self.current_tool = tool
        self.layout = QFormLayout(self)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        
        # Style for input widgets
        input_style = "font-size: 16px; padding: 8px; min-height: 50px;"
        
        self.id_edit = QLineEdit(tool.id if tool else "")
        self.id_edit.setEnabled(not tool) # ID not editable
        self.id_edit.setStyleSheet(input_style)
        self.id_edit.setMinimumWidth(300)
        self.layout.addRow("ID:", self.id_edit)
        
        self.name_edit = QLineEdit(tool.name if tool else "")
        self.name_edit.setStyleSheet(input_style)
        self.name_edit.setMinimumWidth(300)
        self.layout.addRow("Name:", self.name_edit)
        
        self.kasten_spin = QSpinBox()
        self.kasten_spin.setRange(1, 2)
        self.kasten_spin.setValue(tool.kasten if tool else 1)
        self.kasten_spin.setStyleSheet(input_style)
        self.kasten_spin.setMinimumWidth(300)
        self.kasten_spin.valueChanged.connect(self.update_fach_max)
        self.layout.addRow("Kasten (1-2):", self.kasten_spin)
        
        self.lade_spin = QSpinBox()
        self.lade_spin.setRange(1, 15)
        self.lade_spin.setValue(tool.lade if tool else 1)
        self.lade_spin.setStyleSheet(input_style)
        self.lade_spin.setMinimumWidth(300)
        self.lade_spin.valueChanged.connect(self.update_fach_max)
        self.layout.addRow("Lade (1-15):", self.lade_spin)
        
        self.fach_spin = QSpinBox()
        self.fach_spin.setRange(1, 99)
        self.fach_spin.setValue(tool.fach if tool else 1)
        self.fach_spin.setStyleSheet(input_style)
        self.fach_spin.setMinimumWidth(300)
        self.fach_spin.valueChanged.connect(self.update_fach_availability)
        self.layout.addRow("Fach:", self.fach_spin)
        
        # Info label for max fach
        self.fach_info = QLabel("")
        self.fach_info.setStyleSheet("color: #7F8C8D; font-style: italic; font-size: 14px;")
        self.layout.addRow("", self.fach_info)
        
        # Availability warning with better visibility
        self.availability_warning = QLabel("")
        self.availability_warning.setStyleSheet("""
            color: #FFFFFF; 
            font-weight: bold; 
            font-size: 14px;
            background-color: #E74C3C;
            padding: 10px;
            border-radius: 5px;
        """)
        self.availability_warning.setWordWrap(True)
        self.availability_warning.setMinimumHeight(50)
        self.layout.addRow("", self.availability_warning)
        
        self.bestand_spin = QSpinBox()
        self.bestand_spin.setRange(0, 9999)
        self.bestand_spin.setValue(tool.bestand if tool else 0)
        self.bestand_spin.setStyleSheet(input_style)
        self.bestand_spin.setMinimumWidth(300)
        self.layout.addRow("Bestand:", self.bestand_spin)
        
        self.min_spin = QSpinBox()
        self.min_spin.setRange(0, 9999)
        self.min_spin.setValue(tool.min_bestand if tool else 0)
        self.min_spin.setStyleSheet(input_style)
        self.min_spin.setMinimumWidth(300)
        self.layout.addRow("Min. Bestand:", self.min_spin)
        
        # Buttons with larger size
        btns = QHBoxLayout()
        btns.setSpacing(10)
        ok_btn = QPushButton("Speichern")
        ok_btn.setMinimumHeight(60)
        ok_btn.setStyleSheet("font-size: 16px; font-weight: bold; background-color: #27AE60; color: white;")
        ok_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.setMinimumHeight(60)
        cancel_btn.setStyleSheet("font-size: 16px;")
        cancel_btn.clicked.connect(self.reject)
        
        btns.addWidget(ok_btn)
        btns.addWidget(cancel_btn)
        self.layout.addRow(btns)
        
        # Initial update
        self.update_fach_max()

    def update_fach_max(self):
        """Update the max Fach value based on drawer configuration."""
        if not self.data_manager:
            return
            
        kasten = self.kasten_spin.value()
        lade = self.lade_spin.value()
        
        rows, cols = self.data_manager.get_drawer_grid(kasten, lade)
        max_fach = rows * cols
        
        self.fach_spin.setMaximum(max_fach)
        self.fach_info.setText(f"Max. Fach für K{kasten}/L{lade}: {max_fach} ({rows}x{cols})")
        
        # Also update availability when drawer changes
        self.update_fach_availability()
        
    def update_fach_availability(self):
        """Check if the selected compartment is already occupied."""
        if not self.data_manager:
            return
            
        kasten = self.kasten_spin.value()
        lade = self.lade_spin.value()
        fach = self.fach_spin.value()
        
        # Ignore current tool's location when editing
        ignore_id = self.current_tool.id if self.current_tool else None
        
        is_available = self.data_manager.check_location_availability(kasten, lade, fach, ignore_id)
        
        if not is_available:
            # Find which tool is in this location
            tools = self.data_manager.load_ruestwerkzeuge()
            occupying_tool = None
            for t in tools:
                if t.id != ignore_id and t.kasten == kasten and t.lade == lade and t.fach == fach:
                    occupying_tool = t
                    break
            
            if occupying_tool:
                self.availability_warning.setText(
                    f"⚠️ BELEGT\n'{occupying_tool.name}'\n(ID: {occupying_tool.id})"
                )
            else:
                self.availability_warning.setText("⚠️ Dieses Fach ist bereits belegt!")
            
            # Red background for occupied
            self.availability_warning.setStyleSheet("""
                color: #FFFFFF; 
                font-weight: bold; 
                font-size: 14px;
                background-color: #E74C3C;
                padding: 10px;
                border-radius: 5px;
            """)
        else:
            self.availability_warning.setText("✓ Fach verfügbar")
            # Green background for available
            self.availability_warning.setStyleSheet("""
                color: #FFFFFF; 
                font-weight: bold; 
                font-size: 14px;
                background-color: #27AE60;
                padding: 10px;
                border-radius: 5px;
            """)

        
    def accept(self):
        """Override accept to validate Fach range."""
        if not self.data_manager:
            super().accept()
            return
            
        kasten = self.kasten_spin.value()
        lade = self.lade_spin.value()
        fach = self.fach_spin.value()
        
        rows, cols = self.data_manager.get_drawer_grid(kasten, lade)
        max_fach = rows * cols
        
        if fach > max_fach:
            QMessageBox.warning(
                self, 
                "Ungültiges Fach", 
                f"Fach {fach} ist nicht verfügbar.\n"
                f"Kasten {kasten}, Lade {lade} hat nur {max_fach} Fächer ({rows}x{cols})."
            )
            return
        
        # Check if location is available (will be caught by data_manager, but good UX to check here too)
        ignore_id = self.current_tool.id if self.current_tool else None
        if not self.data_manager.check_location_availability(kasten, lade, fach, ignore_id):
            QMessageBox.warning(
                self,
                "Fach belegt",
                f"Das Fach K{kasten}/L{lade}/F{fach} ist bereits mit einem anderen Werkzeug belegt.\n"
                f"Bitte wählen Sie ein anderes Fach."
            )
            return
            
        super().accept()
        
    def get_data(self):
        return {
            'id': self.id_edit.text(),
            'name': self.name_edit.text(),
            'kasten': self.kasten_spin.value(),
            'lade': self.lade_spin.value(),
            'fach': self.fach_spin.value(),
            'bestand': self.bestand_spin.value(),
            'min_bestand': self.min_spin.value()
        }


