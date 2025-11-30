from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                               QMessageBox, QGroupBox, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QAbstractItemView, QHBoxLayout, QLineEdit)
from ...daten_manager import DataManager
from ...authentifizierung import AuthManager
from ..benutzer_verwaltung import UserManagementDialog
from ..werkzeug_dialog import ToolDialog

class AdminPage(QWidget):
    def __init__(self, data_manager: DataManager, auth_manager: AuthManager, parent_window=None):
        super().__init__()
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.parent_window = parent_window # To trigger global refresh if needed
        self.all_tools = []  # Store all tools for filtering
        
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)
        
        # Header
        label = QLabel("Admin")
        label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1ABC9C; margin-bottom: 10px;")
        layout.addWidget(label)
        
        # Search Field (Top)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Suche...")
        self.search_input.setMinimumHeight(60)
        self.search_input.setStyleSheet("font-size: 18px; padding: 10px;")
        self.search_input.textChanged.connect(self.filter_tools)
        layout.addWidget(self.search_input)
        
        # User Management
        user_group = QGroupBox("Benutzerverwaltung")
        user_layout = QVBoxLayout()
        user_btn = QPushButton("Benutzer verwalten")
        user_btn.setMinimumHeight(60)
        user_btn.clicked.connect(self.open_benutzer_verwaltung)
        user_layout.addWidget(user_btn)
        user_group.setLayout(user_layout)
        layout.addWidget(user_group)
        
        # Tool Management
        tool_group = QGroupBox("Werkzeugverwaltung")
        tool_layout = QVBoxLayout()
        
        # Buttons
        btn_layout = QHBoxLayout()
        add_tool_btn = QPushButton("Neues Werkzeug anlegen")
        add_tool_btn.setMinimumHeight(60)
        add_tool_btn.clicked.connect(self.add_tool)
        btn_layout.addWidget(add_tool_btn)
        
        edit_tool_btn = QPushButton("Werkzeug bearbeiten")
        edit_tool_btn.setMinimumHeight(60)
        edit_tool_btn.clicked.connect(self.edit_tool)
        btn_layout.addWidget(edit_tool_btn)
        
        reset_btn = QPushButton("Werkzeugkästen zurücksetzen")
        reset_btn.setMinimumHeight(60)
        reset_btn.setStyleSheet("background-color: #d9534f; color: white;")
        reset_btn.clicked.connect(self.reset_toolboxes)
        btn_layout.addWidget(reset_btn)
        
        del_tool_btn = QPushButton("Werkzeug löschen")
        del_tool_btn.setMinimumHeight(60)
        del_tool_btn.setStyleSheet("background-color: #c0392b; color: white;")
        del_tool_btn.clicked.connect(self.delete_tool)
        btn_layout.addWidget(del_tool_btn)
        
        tool_layout.addLayout(btn_layout)
        
        # Table
        self.tool_table = QTableWidget()
        self.tool_table.setColumnCount(4)
        self.tool_table.setHorizontalHeaderLabels(["ID", "Name", "Status", "Lagerplatz"])
        
        # Configure column widths - Name gets more space
        header = self.tool_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Name - takes most space
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Lagerplatz
        
        self.tool_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tool_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tool_table.verticalHeader().setDefaultSectionSize(60)  # Smaller row height
        self.tool_table.setShowGrid(True)
        self.tool_table.setAlternatingRowColors(True)
        self.tool_table.setStyleSheet("QTableWidget::item { font-size: 14px; }")
        self.tool_table.doubleClicked.connect(self.edit_tool)
        tool_layout.addWidget(self.tool_table)
        
        tool_group.setLayout(tool_layout)
        layout.addWidget(tool_group)
        
        self.refresh_data()
        
        # Remove the stretch to make table bigger
        # layout.addStretch()
        self.setLayout(layout)
        
    def open_benutzer_verwaltung(self):
        dialog = UserManagementDialog(self.data_manager, self)
        dialog.exec()
        
    def refresh_data(self):
        self.all_tools = self.data_manager.load_tools()
        self.update_table(self.all_tools)
    
    def update_table(self, tools):
        self.tool_table.setRowCount(len(tools))
        
        # Sort by ID (numeric if possible)
        try:
            tools.sort(key=lambda t: float(t.id.replace(',', '.')) if t.id.replace(',', '.').replace('.', '', 1).isdigit() else float('inf'))
        except:
            pass # Keep original order if sort fails
            
        for i, tool in enumerate(tools):
            self.tool_table.setItem(i, 0, QTableWidgetItem(str(tool.id)))
            self.tool_table.setItem(i, 1, QTableWidgetItem(tool.name))
            self.tool_table.setItem(i, 2, QTableWidgetItem(tool.status))
            self.tool_table.setItem(i, 3, QTableWidgetItem(tool.lagerplatz))
    
    def filter_tools(self):
        query = self.search_input.text().lower()
        
        if not query:
            self.update_table(self.all_tools)
            return
        
        filtered = []
        for tool in self.all_tools:
            # Search in ID, Name, Status, and Lagerplatz
            if (query in tool.id.lower() or 
                query in tool.name.lower() or 
                query in tool.status.lower() or 
                query in str(tool.lagerplatz).lower()):
                filtered.append(tool)
        
        self.update_table(filtered)

    def add_tool(self):
        # Erstelle Dialog einmal
        dialog = ToolDialog(self, data_manager=self.data_manager)
        
        # Schleife für Validierung
        while True:
            if dialog.exec():
                new_tool = dialog.get_data()
                tools = self.data_manager.load_tools()
                
                # Prüfe ob ID bereits existiert
                if any(t.id == new_tool.id for t in tools):
                    # Zeige Warnung OHNE Dialog zu schließen
                    response = QMessageBox.warning(
                        self, 
                        "ID bereits vergeben", 
                        f"Die ID '{new_tool.id}' existiert bereits!\n\n"
                        "Bitte ändern Sie die ID und versuchen Sie es erneut.\n\n"
                        "Klicken Sie auf 'OK' um die ID zu ändern oder 'Abbrechen' um den Vorgang abzubrechen.",
                        QMessageBox.Ok | QMessageBox.Cancel
                    )
                    
                    if response == QMessageBox.Ok:
                        # Dialog erneut anzeigen mit den bisherigen Daten
                        # Erstelle neuen Dialog mit den eingegebenen Daten
                        dialog = ToolDialog(self, new_tool, self.data_manager)
                        # ID-Feld wieder editierbar machen (da es ein "neues" Werkzeug ist)
                        dialog.id_input.setReadOnly(False)
                        dialog.id_input.selectAll()  # Markiere ID für einfaches Überschreiben
                        dialog.id_input.setFocus()
                        continue  # Wiederhole Schleife
                    else:
                        # Benutzer hat abgebrochen
                        break
                
                # Alles OK - Werkzeug hinzufügen
                tools.append(new_tool)
                self.data_manager.save_tools(tools)
                
                # Wenn Status "Rüstwerkzeuge" ist, auch in ruestwerkzeuge.csv eintragen
                if new_tool.status == "Rüstwerkzeuge":
                    from ...modelle import Ruestwerkzeug
                    
                    # Erstelle Rüstwerkzeug-Eintrag mit leeren Standardwerten
                    # Der Lagerplatz muss später manuell zugewiesen werden
                    ruest = Ruestwerkzeug(
                        id=new_tool.id,
                        name=new_tool.name,
                        kasten=0,      # Muss manuell zugewiesen werden
                        lade=0,        # Muss manuell zugewiesen werden
                        fach=0,        # Muss manuell zugewiesen werden
                        bestand=0,     # Standard: Bestand 0
                        min_bestand=0  # Standard: MinBestand 0
                    )
                    
                    try:
                        # Versuche Rüstwerkzeug hinzuzufügen
                        success = self.data_manager.add_ruestwerkzeug(ruest)
                        if success:
                            QMessageBox.information(
                                self, 
                                "Erfolg", 
                                f"Werkzeug angelegt.\n\n"
                                f"Das Werkzeug wurde auch als Rüstwerkzeug eingetragen.\n"
                                f"Bitte weisen Sie den Lagerplatz (Kasten/Lade/Fach) im Rüstwerkzeug-Bereich zu!"
                            )
                        else:
                            # ID existiert bereits in Rüstwerkzeuge (sollte theoretisch nicht passieren)
                            QMessageBox.warning(
                                self,
                                "Teilweise erfolgreich",
                                "Werkzeug wurde angelegt, aber in Rüstwerkzeuge-Liste war diese ID bereits vorhanden."
                            )
                    except ValueError as e:
                        # Fehler beim Hinzufügen (sollte bei K=0/L=0/F=0 nicht passieren)
                        QMessageBox.warning(
                            self,
                            "Teilweise erfolgreich", 
                            f"Werkzeug wurde angelegt, aber konnte nicht in Rüstwerkzeuge eingetragen werden:\n{str(e)}\n\n"
                            f"Bitte tragen Sie das Werkzeug manuell im Rüstwerkzeug-Bereich ein."
                        )
                else:
                    # Normales Werkzeug - Standard-Erfolgsmeldung
                    QMessageBox.information(self, "Erfolg", "Werkzeug angelegt.")
                
                self.refresh_data()
                if self.parent_window:
                    self.parent_window.refresh_all()
                break  # Schleife verlassen
            else:
                # Benutzer hat abgebrochen
                break

    def edit_tool(self):
        selected_items = self.tool_table.selectedItems()
        if not selected_items:
            return
            
        row = selected_items[0].row()
        tool_id = self.tool_table.item(row, 0).text()
        
        tools = self.data_manager.load_tools()
        tool = next((t for t in tools if t.id == tool_id), None)
        
        if tool:
            dialog = ToolDialog(self, tool, self.data_manager)
            if dialog.exec():
                updated_tool = dialog.get_data()
                # Update list
                for i, t in enumerate(tools):
                    if t.id == tool.id:
                        tools[i] = updated_tool
                        break
                
                self.data_manager.save_tools(tools)
                self.refresh_data()
                if self.parent_window:
                    self.parent_window.refresh_all()

    def delete_tool(self):
        selected_items = self.tool_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Auswahl", "Bitte wählen Sie ein Werkzeug zum Löschen aus.")
            return
            
        row = selected_items[0].row()
        tool_id = self.tool_table.item(row, 0).text()
        tool_name = self.tool_table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self, 
            "Löschen bestätigen", 
            f"Möchten Sie das Werkzeug '{tool_name}' (ID: {tool_id}) wirklich löschen?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.data_manager.delete_tool(tool_id):
                self.refresh_data()
                if self.parent_window:
                    self.parent_window.refresh_all()
                QMessageBox.information(self, "Erfolg", f"Werkzeug '{tool_name}' wurde gelöscht.")
            else:
                QMessageBox.warning(self, "Fehler", "Werkzeug konnte nicht gelöscht werden.")

    def reset_toolboxes(self):
        reply = QMessageBox.question(self, "Zurücksetzen bestätigen", 
                                     "Möchten Sie wirklich alle Werkzeugkästen auf Werkseinstellungen zurücksetzen? Alle Maschinenbelegungen werden gelöscht.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            tools = self.data_manager.load_tools()
            for tool in tools:
                # Clear per-box status and machine assignment
                keys_to_remove = []
                for k in tool.extra_data.keys():
                    if k.startswith('Status_Box_') or k.startswith('Maschine_Box_'):
                        keys_to_remove.append(k)
                
                for k in keys_to_remove:
                    del tool.extra_data[k]
                
                # Reset global status if it was 'maschine'
                if tool.status.lower() == 'maschine':
                    tool.status = 'frei'
                
                # Clear global machine/origin data
                if 'Maschine' in tool.extra_data:
                    del tool.extra_data['Maschine']
                if 'Herkunft_Kasten' in tool.extra_data:
                    del tool.extra_data['Herkunft_Kasten']
            
            self.data_manager.save_tools(tools)
            self.refresh_data()
            QMessageBox.information(self, "Erfolg", "Alle Werkzeugkästen wurden zurückgesetzt.")
            if self.parent_window:
                self.parent_window.refresh_all()
