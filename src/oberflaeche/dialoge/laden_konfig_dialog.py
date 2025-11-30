from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QComboBox, QSpinBox, QPushButton, QMessageBox, QGroupBox, QFormLayout)
from PySide6.QtCore import Qt
from ...daten_manager import DataManager

class DrawerConfigDialog(QDialog):
    def __init__(self, data_manager: DataManager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ladenkonfiguration")
        self.setFixedSize(400, 300)
        self.data_manager = data_manager
        self.current_config = self.data_manager.load_drawer_config()
        
        layout = QVBoxLayout(self)
        
        # Selection Group
        sel_group = QGroupBox("Lade auswählen")
        sel_layout = QFormLayout(sel_group)
        
        self.kasten_combo = QComboBox()
        self.kasten_combo.addItems(["1", "2"])
        self.kasten_combo.currentIndexChanged.connect(self.load_current_settings)
        sel_layout.addRow("Kasten:", self.kasten_combo)
        
        self.lade_combo = QComboBox()
        self.lade_combo.addItems([str(i) for i in range(1, 16)]) # 1-15
        self.lade_combo.currentIndexChanged.connect(self.load_current_settings)
        sel_layout.addRow("Lade:", self.lade_combo)
        
        layout.addWidget(sel_group)
        
        # Configuration Group
        config_group = QGroupBox("Raster Einstellungen")
        config_layout = QFormLayout(config_group)
        
        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(1, 20)
        self.rows_spin.setValue(4)
        config_layout.addRow("Reihen (Tiefe):", self.rows_spin)
        
        self.cols_spin = QSpinBox()
        self.cols_spin.setRange(1, 20)
        self.cols_spin.setValue(6)
        config_layout.addRow("Spalten (Breite):", self.cols_spin)
        
        layout.addWidget(config_group)
        
        # Info Label
        self.info_label = QLabel("Gesamt Fächer: 24")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("color: #7F8C8D; font-style: italic;")
        layout.addWidget(self.info_label)
        
        # Connect spins to update info
        self.rows_spin.valueChanged.connect(self.update_info)
        self.cols_spin.valueChanged.connect(self.update_info)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Speichern")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet("background-color: #27AE60; color: white; font-weight: bold; padding: 8px;")
        
        close_btn = QPushButton("Schließen")
        close_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
        # Initial load
        self.load_current_settings()

    def load_current_settings(self):
        kasten = self.kasten_combo.currentText()
        lade = self.lade_combo.currentText()
        
        rows = 4
        cols = 6
        
        if kasten in self.current_config and lade in self.current_config[kasten]:
            cfg = self.current_config[kasten][lade]
            rows = cfg.get('rows', 4)
            cols = cfg.get('cols', 6)
            
        self.rows_spin.blockSignals(True)
        self.cols_spin.blockSignals(True)
        self.rows_spin.setValue(rows)
        self.cols_spin.setValue(cols)
        self.rows_spin.blockSignals(False)
        self.cols_spin.blockSignals(False)
        
        self.update_info()

    def update_info(self):
        rows = self.rows_spin.value()
        cols = self.cols_spin.value()
        self.info_label.setText(f"Gesamt Fächer: {rows * cols}")

    def save_settings(self):
        kasten = self.kasten_combo.currentText()
        lade = self.lade_combo.currentText()
        rows = self.rows_spin.value()
        cols = self.cols_spin.value()
        
        if kasten not in self.current_config:
            self.current_config[kasten] = {}
            
        self.current_config[kasten][lade] = {
            "rows": rows,
            "cols": cols
        }
        
        try:
            self.data_manager.save_drawer_config(self.current_config)
            QMessageBox.information(self, "Gespeichert", f"Konfiguration für Kasten {kasten}, Lade {lade} gespeichert.")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern: {e}")
