from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                               QPushButton, QLabel, QComboBox, QMessageBox, QAbstractItemView, QListWidgetItem, QLineEdit)
from PySide6.QtCore import Qt
from ...daten_manager import DataManager
from ...authentifizierung import AuthManager

class ToolboxPage(QWidget):
    def __init__(self, data_manager: DataManager, auth_manager: AuthManager):
        super().__init__()
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.tools = []
        self.available_tools = []  # Store filtered tools for search
        self.machines = ["Hermle40", "Hermle400", "Evo60", "EVO100", "650V"]
        
        self.init_ui()

    def init_ui(self):
        # Main Layout (Vertical)
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Header
        header = QLabel("Werkzeugkasten")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1ABC9C; margin-bottom: 10px;")
        main_layout.addWidget(header)
        
        # Search Bar (Top)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Suche...")
        self.search_input.setMinimumHeight(60)
        self.search_input.setStyleSheet("font-size: 18px; padding: 10px;")
        self.search_input.textChanged.connect(self.filter_left_list)
        main_layout.addWidget(self.search_input)
        
        # Content Layout (Horizontal 3-Col)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(40)
        
        # --- Left Side: Toolbox Selection & Available Tools ---
        left_container = QWidget()
        left_container.setObjectName("card") # Premium Card Style
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(25, 25, 25, 25)
        left_layout.setSpacing(15)
        
        # Header
        left_header_box = QHBoxLayout()
        from ..icon_manager import icon_manager
        left_icon = QLabel()
        left_icon.setPixmap(icon_manager.get_pixmap('werkzeugkasten', 64))
        left_icon.setStyleSheet("background: transparent;")
        left_header = QLabel("WERKZEUGKÄSTEN")
        left_header.setObjectName("header")
        left_header_box.addWidget(left_icon)
        left_header_box.addWidget(left_header)
        left_header_box.addStretch()
        
        # Toolbox Selector
        self.toolbox_selector = QComboBox()
        self.toolbox_selector.addItems([f"Werkzeugkasten {i}" for i in range(1, 5)])
        self.toolbox_selector.setFixedHeight(180) # Larger for touch - closed state
        self.toolbox_selector.setStyleSheet("""
            QComboBox {
                background-color: #2C3E50;
                color: #BDC3C7;
                font-size: 20px; 
                padding: 15px;
                font-weight: bold;
                border: 2px solid white;
                border-radius: 8px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 2px solid white;
                border-bottom: 2px solid white;
                width: 10px;
                height: 10px;
                margin-right: 15px;
                transform: rotate(-45deg);
            }
            QComboBox QAbstractItemView {
                background-color: #2C3E50;
                color: #BDC3C7;
                font-size: 18px;
                selection-background-color: #1ABC9C;
            }
            QComboBox QAbstractItemView::item {
                min-height: 80px;
                padding: 15px;
            }
        """)
        # Set custom view for dropdown items
        from PySide6.QtWidgets import QListView, QStyledItemDelegate
        from PySide6.QtCore import QSize
        
        list_view = QListView()
        list_view.setStyleSheet("""
            QListView {
                background-color: #2C3E50;
                color: #BDC3C7;
                outline: none;
            }
            QListView::item { 
                min-height: 80px; 
                padding: 15px; 
                font-size: 18px; 
            }
            QListView::item:selected {
                background-color: #1ABC9C;
                color: white;
            }
        """)
        self.toolbox_selector.setView(list_view)
        
        class ItemDelegate(QStyledItemDelegate):
            def sizeHint(self, option, index):
                size = super().sizeHint(option, index)
                size.setHeight(80)
                return size
        
        self.toolbox_selector.setItemDelegate(ItemDelegate())
        self.toolbox_selector.currentIndexChanged.connect(self.update_left_view)
        
        # Available Tools List
        self.left_list = QListWidget()
        self.left_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.left_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.left_list.setAlternatingRowColors(True)
        self.left_list.setStyleSheet("QListWidget::item { font-size: 18px; min-height: 60px; }")
        
        left_layout.addLayout(left_header_box)
        left_layout.addWidget(self.toolbox_selector)
        left_layout.addWidget(self.left_list)
        
        # --- Center: Action Buttons ---
        center_layout = QVBoxLayout()
        center_layout.addStretch()
        
        # Load Button (Red Gradient)
        self.btn_load = QPushButton("→\nLADEN")
        self.btn_load.setObjectName("primaryButton") # Uses the premium gradient
        self.btn_load.setFixedSize(160, 160)
        self.btn_load.setCursor(Qt.PointingHandCursor)
        self.btn_load.clicked.connect(self.move_to_machine)
        
        # Unload Button (Dark)
        self.btn_unload = QPushButton("←\nENTLADEN")
        self.btn_unload.setFixedSize(160, 160)
        self.btn_unload.setCursor(Qt.PointingHandCursor)
        self.btn_unload.clicked.connect(self.move_to_toolbox)
        
        center_layout.addWidget(self.btn_load)
        center_layout.addSpacing(30)
        center_layout.addWidget(self.btn_unload)
        center_layout.addStretch()

        # --- Right Side: Machine Selection & Loaded Tools ---
        right_container = QWidget()
        right_container.setObjectName("card") # Premium Card Style
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(25, 25, 25, 25)
        right_layout.setSpacing(15)
        
        # Header
        right_header_box = QHBoxLayout()
        right_icon = QLabel() 
        right_icon.setPixmap(icon_manager.get_pixmap('maschine', 64))
        right_icon.setStyleSheet("background: transparent;")
        right_header = QLabel("MASCHINE")
        right_header.setObjectName("header")
        right_header_box.addWidget(right_icon)
        right_header_box.addWidget(right_header)
        right_header_box.addStretch()
        
        # Machine Selector
        self.machine_selector = QComboBox()
        self.machine_selector.addItems(self.machines)
        self.machine_selector.setFixedHeight(180) # Larger for touch - closed state (same as toolbox)
        self.machine_selector.setStyleSheet("""
            QComboBox {
                background-color: #2C3E50;
                color: #BDC3C7;
                font-size: 20px; 
                padding: 15px;
                font-weight: bold;
                border: 2px solid white;
                border-radius: 8px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 2px solid white;
                border-bottom: 2px solid white;
                width: 10px;
                height: 10px;
                margin-right: 15px;
                transform: rotate(-45deg);
            }
            QComboBox QAbstractItemView {
                background-color: #2C3E50;
                color: #BDC3C7;
                font-size: 18px;
                selection-background-color: #1ABC9C;
            }
            QComboBox QAbstractItemView::item {
                min-height: 80px;
                padding: 15px;
            }
        """)
        # Set custom view for dropdown items
        from PySide6.QtWidgets import QListView, QStyledItemDelegate
        
        machine_list_view = QListView()
        machine_list_view.setStyleSheet("""
            QListView {
                background-color: #2C3E50;
                color: #BDC3C7;
                outline: none;
            }
            QListView::item { 
                min-height: 80px; 
                padding: 15px; 
                font-size: 18px; 
            }
            QListView::item:selected {
                background-color: #1ABC9C;
                color: white;
            }
        """)
        self.machine_selector.setView(machine_list_view)
        
        class MachineItemDelegate(QStyledItemDelegate):
            def sizeHint(self, option, index):
                size = super().sizeHint(option, index)
                size.setHeight(80)
                return size
        
        self.machine_selector.setItemDelegate(MachineItemDelegate())
        self.machine_selector.currentIndexChanged.connect(self.update_right_view)
        
        # Machine Tools List
        self.right_list = QListWidget()
        self.right_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.right_list.setAlternatingRowColors(True)
        self.right_list.setStyleSheet("QListWidget::item { font-size: 18px; min-height: 60px; }")
        
        # Empty State Label
        self.empty_state_label = QLabel("Keine Werkzeuge\nin dieser Maschine")
        self.empty_state_label.setAlignment(Qt.AlignCenter)
        self.empty_state_label.setStyleSheet("color: #444; font-size: 18px; font-weight: bold; margin-top: 50px; background: transparent;")
        self.empty_state_label.hide()
        
        right_layout.addLayout(right_header_box)
        right_layout.addWidget(self.machine_selector)
        right_layout.addWidget(self.right_list)
        right_layout.addWidget(self.empty_state_label)

        # Add layouts to content layout
        content_layout.addWidget(left_container, 40)
        content_layout.addLayout(center_layout, 20)
        content_layout.addWidget(right_container, 40)
        
        main_layout.addLayout(content_layout)

    def refresh_data(self):
        self.tools = self.data_manager.load_tools()
        self.update_left_view()
        self.update_right_view()

    def update_left_view(self):
        self.left_list.clear()
        
        current_box_idx = self.toolbox_selector.currentIndex() + 1
        status_key = f'Status_Box_{current_box_idx}'
        
        available_tools = []
        for t in self.tools:
            box_status = t.extra_data.get(status_key, t.status)
            if box_status.lower() == 'maschine':
                continue
            if t.status.lower() != 'gerüstet':
                continue
            available_tools.append(t)
        
        # Sort by POS
        def sort_key(t):
            pos = t.lagerplatz if t.lagerplatz else "ZZZ"
            if pos.isdigit():
                return (0, int(pos), t.id)
            try:
                return (0, float(pos.replace(',', '.')), t.id)
            except ValueError:
                pass
            return (1, pos, t.id)

        available_tools.sort(key=sort_key)
        
        # Store for filtering
        self.available_tools = available_tools
        
        for tool in available_tools:
            # Format: "001   DEPO-D42R6"
            pos_str = str(tool.lagerplatz).zfill(3) if tool.lagerplatz and tool.lagerplatz.isdigit() else str(tool.lagerplatz)
            display_text = f"{pos_str:<6} {tool.name}"
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, {'name': tool.name, 'pos': tool.lagerplatz})
            self.left_list.addItem(item)
    
    def filter_left_list(self):
        """Filter the left list based on search query"""
        query = self.search_input.text().lower()
        self.left_list.clear()
        
        if not query:
            # Show all available tools
            tools_to_show = self.available_tools
        else:
            # Filter tools
            tools_to_show = []
            for tool in self.available_tools:
                if (query in tool.name.lower() or 
                    query in str(tool.lagerplatz).lower() or
                    query in tool.id.lower()):
                    tools_to_show.append(tool)
        
        # Display filtered tools
        for tool in tools_to_show:
            pos_str = str(tool.lagerplatz).zfill(3) if tool.lagerplatz and tool.lagerplatz.isdigit() else str(tool.lagerplatz)
            display_text = f"{pos_str:<6} {tool.name}"
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, {'name': tool.name, 'pos': tool.lagerplatz})
            self.left_list.addItem(item)


    def update_right_view(self):
        self.right_list.clear()
        current_machine = self.machine_selector.currentText()
        
        machine_items = []
        for tool in self.tools:
            for i in range(1, 5):
                m_key = f'Maschine_Box_{i}'
                if tool.extra_data.get(m_key) == current_machine:
                    machine_items.append((tool, i))
        
        machine_items.sort(key=lambda x: x[0].name)
        
        # Always show the list, even if empty
        self.right_list.show()
        self.empty_state_label.hide()
        
        for tool, box_idx in machine_items:
            display_text = f"{tool.name} [Box {box_idx}]"
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, {
                'name': tool.name, 
                'pos': tool.lagerplatz,
                'box': box_idx
            })
            self.right_list.addItem(item)


    def move_to_machine(self):
        items = self.left_list.selectedItems()
        if not items: return
        
        target_machine = self.machine_selector.currentText()
        current_box_idx = self.toolbox_selector.currentIndex() + 1
        status_key = f'Status_Box_{current_box_idx}'
        machine_key = f'Maschine_Box_{current_box_idx}'
        original_status_key = f'OriginalStatus_Box_{current_box_idx}'
        
        for item in items:
            tool_data = item.data(Qt.UserRole)
            if not tool_data: continue
            
            # Find tool by Name + Lagerplatz (ID is only for external programs)
            tool = next((t for t in self.tools 
                        if t.name == tool_data['name'] 
                        and t.lagerplatz == tool_data['pos']), None)
            if tool:
                # Save the ORIGINAL status before changing to 'maschine'
                current_status = tool.extra_data.get(status_key, tool.status)
                tool.extra_data[original_status_key] = current_status
                
                # Set status for THIS toolbox ONLY
                tool.extra_data[status_key] = 'maschine'
                tool.extra_data[machine_key] = target_machine
                
                # DO NOT change tool.status (main Status column)!
                # Only update legacy fields for compatibility
                tool.extra_data['Maschine'] = target_machine
                tool.extra_data['Herkunft_Kasten'] = f"Werkzeugkasten {current_box_idx}"
        
        self.data_manager.save_tools(self.tools)
        self.refresh_data()
        
    def move_to_toolbox(self):
        items = self.right_list.selectedItems()
        if not items: return
        
        for item in items:
            data = item.data(Qt.UserRole)
            if not data: continue
            
            box_idx = data['box']
            
            # Find tool by Name + Lagerplatz (ID is only for external programs)
            tool = next((t for t in self.tools 
                        if t.name == data['name'] 
                        and t.lagerplatz == data['pos']), None)
            if tool:
                # Restore the ORIGINAL status (before it was loaded into machine)
                original_status_key = f'OriginalStatus_Box_{box_idx}'
                original_status = tool.extra_data.get(original_status_key, tool.status)
                
                # Reset status for that specific box to its ORIGINAL value
                tool.extra_data[f'Status_Box_{box_idx}'] = original_status
                
                # Clear the saved original status
                if original_status_key in tool.extra_data:
                    del tool.extra_data[original_status_key]
                
                # Clear machine assignment for that box
                if f'Maschine_Box_{box_idx}' in tool.extra_data:
                    del tool.extra_data[f'Maschine_Box_{box_idx}']
                
                # DO NOT change tool.status (main Status column)!
                # Only clear legacy machine field if no box has it in a machine
                is_in_any_machine = False
                for i in range(1, 5):
                    if tool.extra_data.get(f'Status_Box_{i}') == 'maschine':
                        is_in_any_machine = True
                        break
                
                if not is_in_any_machine:
                    # Clear legacy machine field only
                    if 'Maschine' in tool.extra_data:
                        del tool.extra_data['Maschine']
        
        self.data_manager.save_tools(self.tools)
        self.refresh_data()
