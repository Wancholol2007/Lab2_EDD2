from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLineEdit, QLabel, QComboBox, QMessageBox)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import os
from src.ui.graph_controller import GraphController
from src.graph.graph import Graph

class Interface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mapa de Aeropuertos")
        self.setGeometry(100, 100, 1200, 800)

        self.graph = Graph()
        csv_path = os.path.abspath(os.path.join(os.path.direname(__file__), "..", "dataset", "flights_final.csv"))
        self.controller.load_data(csv_path)
        self.controller = GraphController(self.graph)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        sidebar = QVBoxLayout()

        self.btn_conexidad = QPushButton("Conexidad del grafo")
        self.btn_conexidad.clicked.connect(self.check_conexity)
        self.btn_mst = QPushButton("Peso de MST")
        self.btn_mst.clicked.connect(self.calculate_mst)

        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Buscar aeropuerto")
        self.btn_buscar = QPushButton("Buscar")
        self.btn_buscar.clicked.connect(self.search_airport)
        self.combo_aeropuertos = QComboBox()

        self.btn_info = QPushButton("Mostrar información")
        self.btn_info.clicked.connect(self.show_airport_info)
        self.btn_lejanos = QPushButton("Aeropuertos lejanos")
        self.btn_lejanos.clicked.connect(self.farthest_airports)

        self.input_segundo = QLineEdit()
        self.input_segundo.setPlaceholderText("Buscar segundo aeropuerto")
        self.btn_buscar2 = QPushButton("Buscar segundo")
        self.btn_buscar2.clicked.connect(self.search_second_airport)
        self.combo_aeropuerto2 = QComboBox()
        self.btn_camino_min = QPushButton("Camino mínimo")
        self.btn_camino_min.clicked.connect(self.shortest_path)

        sidebar.addWidget(self.btn_conexidad)
        sidebar.addWidget(self.btn_mst)
        sidebar.addSpacing(20)
        sidebar.addWidget(self.input_buscar)
        sidebar.addWidget(self.btn_buscar)
        sidebar.addWidget(self.combo_aeropuertos)
        sidebar.addSpacing(20)
        sidebar.addWidget(self.btn_info)
        sidebar.addWidget(self.btn_lejanos)
        sidebar.addSpacing(20)
        sidebar.addWidget(self.input_segundo)
        sidebar.addWidget(self.btn_buscar2)
        sidebar.addWidget(self.combo_aeropuerto2)
        sidebar.addWidget(self.btn_camino_min)

        self.map_view = QWebEngineView()

        main_layout.addLayout(sidebar, 1)
        main_layout.addWidget(self.map_view, 3)

        self.show()

    def load_map(self, path):
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), "output", "map.html"))
        self.map_view.setUrl(QUrl.fromLocalFile(path))

    def check_conexity(self):
        connected = self.controller.check_connectivity()
        return connected
    
    def calculate_mst(self):
        total_weight = self.controller.get_mst_weight()
        QMessageBox.information(self, "Peso del árbol de expansión mínima", f"Peso total: {total_weight:.4f}")
    
    def search_airport(self):
        code = self.input_buscar.text()
        airport = self.controller.search_airport(code)

        self.combo_aeropuertos.clear()
        if airport:
            self.combo_aeropuertos.addItem(f"{airport.code} - {airport.city}, {airport.country}")
        else:
            self.combo_aeropuertos.addItem("Aeropuerto no encontrado")

    def show_airport_info(self):
        text = self.combo_aeropuertos.currentText()
        if not text or "no encontrado" in text.lower():
            QMessageBox.warning(self, "Error", "Seleccione un aeropuerto válido")
            return

            code = text.split(" - ")[0]
            airport = self.controller.search_airport(code)

            if airport:
                info = airport.info()
                msg = "\n".join(f"{k}: {v}" for k, v in info.items())
                QMessageBox.information(self, f"Información de {airport.code}", msg)
            else:
                QMessageBox.warning(self, "Error", "No se encontró información del aeropuerto.")
    
    def farthest_airports(self):
        text = self.combo_aeropuertos.currentText()
        if not text or "no encontrado" in text.lower():
            QMessageBox.warning(self, "Error", "Seleccione un aeropuerto válido")
            return
        
        code = text.split(" - ")[0]
        far_list = self.controller.farthest_airports(code)

        if far_list:
            msg = "\n".join(f"{a.code} - {a.city}, {a.country}" for a in far_list)
            QMessageBox.information(self, "Aeropuertos más lejanos", msg)
        else:
            QMessageBox.warning("Sin resultados", "No se encontraron aeropuertos lejanos")
        return
    
    def search_second_airport(self):
        code = self.input_buscar.text()
        airport = self.controller.search_airport(code)

        self.combo_aeropuertos.clear()
        if airport:
            self.combo_aeropuerto2.addItem(f"{airport.code} - {airport.city}, {airport.country}")
        else:
            self.combo_aeropuerto2.addItem("Aeropuerto no encontrado")
    
    def shortest_path(self):
        text1 = self.combo_aeropuertos.currentText()
        text2 = self.combo_aeropuerto2.currentText()

        if not text1 or not text2 or "no encontrado" in text1.lower() or "no encontrado" in text2.lower():
            QMessageBox.warning(self, "Error", "Seleccione ambos aeropuertos correctamente")
            return
        
        code1 = text1.split(" - ")[0]
        code2 = text2.split(" - ")[0]

        path = self.controller.shortest_path(code1, code2)
        if not path:
            QMessageBox.warning(self, "Sin conexión", "No se encontró un camino entre los aeropuertos seleccionados")
            return
        
        msg = " -> ".join(a.code for a in path)
        QMessageBox.information(self, "Camino más corto", f"Ruta: {msg}")
