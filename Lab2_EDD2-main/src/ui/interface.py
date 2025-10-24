from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLineEdit, QLabel, QComboBox, QMessageBox)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import os
from ui.graph_controller import GraphController
from graph.graph import Graph

class Interface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mapa de Aeropuertos")
        self.setGeometry(100, 100, 1200, 800)

        self.graph = Graph()
        self.controller = GraphController(self.graph)
        self.map_view = QWebEngineView()
        self.controller.load_data()
        try:
            map_path = self.controller.generate_map()
            self.load_map(map_path)
        except Exception as e:
            print(f"Error al generar el mapa: {e}")

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

        main_layout.addLayout(sidebar, 1)
        main_layout.addWidget(self.map_view, 3)

        self.show()

    def load_map(self, map_path=None):
        if map_path is None:
            map_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output", "map.html"))
        if os.path.exists(map_path):    
            self.map_view.setUrl(QUrl.fromLocalFile(map_path))
        else:
            print("No se encontró el archivo map.html")

    def check_conexity(self):
        connected = self.controller.check_connectivity()
        if connected:
            QMessageBox.information(self, "Conexidad del grafo", "El grafo es conexo")
        else:
            n, components = self.controller.connected_components()
            msg = f"El grafo es disconexo\nCantidad de componentes conexas: {n}\n\n"
            for i, size in enumerate(components, start=1):
                msg += f"Componente {i}: {size} vértices\n"
            QMessageBox.information(self, "Conexidad del grafo", msg)
    
    def calculate_mst(self):
        try:
            result = self.controller.get_mst_weight()

            if isinstance(result, (int, float)):
                QMessageBox.information(self, "Árbol de Expansión Mínima", f"Peso total del árbol de expansión mínima: {result:.2f}")
                print(f"[INFO] Grafo conexo - Peso total del MST: {result:.2f}")

            elif isinstance(result, dict):
                componentes_info = ""
                for item in result["Componentes"]:
                    componentes_info += (f"Componente {item['Componente']}: Peso total = {item['Peso total']:.2f}\n")
                QMessageBox.information(self, "Árbol de Expansión Mínima por Componentes", componentes_info)
                print(f"[INFO] Grafo disconexo - Peso total global: {result['Peso total global']:.2f}")

            else:
                QMessageBox.warning(self, "Error", "Formato de resultado inesperado del MST.")
                print("[ERROR] Tipo de retorno inesperado en get_mst_weight")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al calcular el árbol de expansión mínima: {e}")
            print(f"[ERROR] Error al calcular MST: {e}")
    
    def search_airport(self):
        code = self.input_buscar.text()
        airport = self.controller.search_airport(code)

        self.combo_aeropuertos.clear()
        if airport:
            self.combo_aeropuertos.addItem(f"{airport.code} - {airport.city}, {airport.country}")
            map_path = self.controller.highlight_airport(airport.code)
            self.load_map(map_path)
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
            map_path = self.controller.show_farthest_airports(code)
            if map_path:
                self.load_map(map_path)

            msg = "\n".join(f"{a.code}: {a.name} - {a.city}, {a.country} ({dist:.2f} km)" for a,dist in far_list)
            QMessageBox.information(self, "Aeropuertos más lejanos", msg)
        else:
            QMessageBox.warning(self, "Sin resultados", "No se encontraron aeropuertos lejanos")
        return
    
    def search_second_airport(self):
        code = self.input_segundo.text()
        airport = self.controller.search_airport(code)

        self.combo_aeropuerto2.clear()
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

        try:
            path, distance = self.controller.shortest_path(code1, code2)
            if path is None:
                print("No se encontró una ruta entre los aeropuertos seleccionados.")
                return
            
            map_path = self.controller.show_shortest_path(path)
            if map_path:
                self.load_map(map_path)

            msg = " -> ".join(a.code for a in path)
            if path:
                msg2 = "\n".join(f"{b.code}: {b.name} - {b.city}, {b.country} ({b.latitude}, {b.longitude})" for b in path)
            QMessageBox.information(self, "Camino mínimo", f"Ruta mas corta\n{msg} \n\n Distancia total: {distance:.2f} km\n\nInformacion de los aeropuertos:\n{msg2}")
        except Exception as e:
            print("Error al generar el mapa: ", e)
