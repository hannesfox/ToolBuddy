
import sys
import os
# Ensure src is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from src.daten_manager import DataManager
from src.authentifizierung import AuthManager
from src.oberflaeche.haupt_fenster import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    data_dir = os.path.join(base_dir, "data")  #Data ordner im programmverzeichnig
    #data_dir = r"D:\MeineDaten\data"           #Date ordner extern speichern 

    tools_csv = os.path.join(data_dir, "werkzeuge.csv")
    users_csv = os.path.join(data_dir, "users.csv")
    
    # Managers
    data_manager = DataManager(tools_csv, users_csv)
    auth_manager = AuthManager(data_manager)
    
    # Login Flow - Auto login as Bediener (as per previous state)
    # If the user wants the login window back, we can add it later, but for now restore functionality
    auth_manager.login("Bediener", "")
    
    # Instantiate Main Window with Managers
    window = MainWindow(data_manager, auth_manager)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
