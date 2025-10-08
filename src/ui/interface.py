from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLineEdit, QLabel, QComboBox)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import os
from src.ui.graph_controller import GraphController


class Interface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mapa de Aeropuertos")
        self.setGeometry(100, 100, 1200, 800)

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
        return total_weight
    
    def search_airport(self):
        airport = self.controller.search_airport()
        return airport if airport is not None else None
    
    def show_airport_info():
        return
    
    def farthest_airports():
        return
    
    def search_second_airport():
        return
    
    def shortest_path():
        return
    