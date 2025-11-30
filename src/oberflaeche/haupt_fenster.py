
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget
from src.oberflaeche.stile import ModernStyles
from src.oberflaeche.komponenten.seitenleiste import Sidebar
from src.oberflaeche.komponenten.uebersicht import Dashboard
from src.oberflaeche.komponenten.werkzeugleiste import Toolbar

# Import Pages
from src.oberflaeche.seiten.werkzeugkasten_seite import ToolboxPage
from src.oberflaeche.seiten.ruestwerkzeug_seite import RuestwerkzeugPage
from src.oberflaeche.seiten.admin_seite import AdminPage
from src.oberflaeche.seiten.detaillierte_suche import DetailedSearchPage

class MainWindow(QMainWindow):
    def __init__(self, data_manager, auth_manager):
        super().__init__()
        self.setWindowTitle("ToolBuddy")
        self.resize(1800, 860)
        
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        
        # Apply Global Styles
        self.setStyleSheet(ModernStyles.get_stylesheet())
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main Layout (Vertical: Content + Toolbar)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Content Layout (Horizontal: Sidebar + Stack)
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = Sidebar(self.auth_manager)
        self.sidebar.page_selected.connect(self.switch_page)
        self.sidebar.login_changed.connect(self.on_login_changed)
        content_layout.addWidget(self.sidebar)
        
        # Stacked Widget for Pages
        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack)
        
        # --- Initialize Pages ---
        
        # 0. Dashboard
        self.dashboard = Dashboard()
        self.dashboard.page_selected.connect(self.switch_page)
        self.stack.addWidget(self.dashboard)
        
        # 1. Werkzeugkasten (ToolboxPage)
        self.toolbox_page = ToolboxPage(self.data_manager, self.auth_manager)
        self.stack.addWidget(self.toolbox_page)
        
        # 2. Rüstwerkzeug (RuestwerkzeugPage)
        self.ruestwerkzeug_page = RuestwerkzeugPage(self.data_manager, self.auth_manager)
        self.stack.addWidget(self.ruestwerkzeug_page)
        
        # 3. Admin (AdminPage)
        self.admin_page = AdminPage(self.data_manager, self.auth_manager, parent_window=self)
        self.stack.addWidget(self.admin_page)
        
        # 4. Suche (DetailedSearchPage)
        self.search_page = DetailedSearchPage(self.data_manager)
        self.stack.addWidget(self.search_page)
        
        # Add Content to Main Layout
        main_layout.addLayout(content_layout)
        
        # Toolbar (Bottom)
        self.toolbar = Toolbar()
        main_layout.addWidget(self.toolbar)
        
    def switch_page(self, page_name):
        """Switch the stacked widget to the requested page."""
        if page_name == "Dashboard":
            self.stack.setCurrentIndex(0)
        elif page_name == "Werkzeugkasten":
            self.toolbox_page.refresh_data()
            self.stack.setCurrentIndex(1)
        elif page_name == "Rüstwerkzeug":
            self.ruestwerkzeug_page.refresh_data()
            self.stack.setCurrentIndex(2)
        elif page_name == "Admin":
            # Check if user has permission to access admin page
            if self.auth_manager.is_admin():
                self.admin_page.refresh_data()
                self.stack.setCurrentIndex(3)
            else:
                # Show error message
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Zugriff verweigert", 
                    "Sie haben keine Berechtigung für den Admin-Bereich!\n\n"
                    "Bitte melden Sie sich als Administrator an.")
                # Stay on current page
        elif page_name == "Suche":
            self.search_page.refresh_data()
            self.stack.setCurrentIndex(4)
            
    def on_login_changed(self):
        """Handle login status changes - update page access."""
        # If user logs out or changes, go back to dashboard
        self.stack.setCurrentIndex(0)
        # Refresh all pages with new user context
        self.refresh_all()
    
    def refresh_all(self):
        """Refresh all pages data."""
        self.toolbox_page.refresh_data()
        self.ruestwerkzeug_page.refresh_data()
        self.admin_page.refresh_data()
        self.search_page.refresh_data()
