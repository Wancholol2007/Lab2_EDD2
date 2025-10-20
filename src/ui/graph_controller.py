import folium
import os

class GraphController:
    def __init__(self, graph):
        self.graph = graph
        self.selected_airports = []
    
    def load_data(self):
        self.graph.load_from_csv("flights_final.csv")
    
    def check_connectivity(self):
        return self.graph.is_connected()
    
    def connected_components(self):
        components = self.graph.get_connected_components()
        cant = len(components)
        vert = []
        if components:
            for a in components:
                vert.append(len(a))

        return cant, vert
    
    def get_mst_weight(self):
        if self.graph.is_connected():
            edges, total_weight = self.graph.kruskal()
            return total_weight
        else:
            results = self.graph.kruskal_por_componentes()
            peso_global = sum(item["Peso total"] for item in results)
            return {"Componentes": results, "Peso total global": peso_global}

    
    def search_airport(self, code):
        cod = code.strip().upper()
        for airport in self.graph.vertices.values():
            if airport.code == cod:
                return airport
        return None
    
    def farthest_airports(self, code):
        return self.graph.far_airports(code)
    
    def shortest_path(self, code1, code2):
        return self.graph.shortest_path(code1, code2)
    
    def generate_map(self, output_path="src/output/map.html"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.abspath(os.path.join(base_dir, ".."))
        output_dir = os.path.join(src_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        map_path = os.path.join(output_dir, "map.html")

        if not self.graph.vertices:
            print("Error: No hay aeropuertos cargados.")
            return None

        latitudes = [a.latitude for a in self.graph.vertices.values()]
        longitudes = [a.longitude for a in self.graph.vertices.values()]
        center_lat = sum(latitudes) / len(latitudes)
        center_lon = sum(longitudes) / len(longitudes)

        m = folium.Map(location=[center_lat, center_lon], zoom_start=3)

        for airport in self.graph.vertices.values():
            folium.Marker(location=[airport.latitude, airport.longitude], popup=f"<b>{airport.code}</b><br>{airport.city}, {airport.country}", tooltip=airport.name, icon=folium.Icon(color="blue", icon="plane", prefix="fa")).add_to(m)

        m.save(map_path)

        print(f"[INFO] Mapa generado en: {map_path}")
        return map_path
    
    def highlight_airports(self, selected_airports = None, path_airports = None, output_path = "src/output/map.html"):
        m = self.generate_map(output_path)

        selected_airports = selected_airports or []
        path_airports = path_airports or []

        for airport in selected_airports:
            folium.Marker(location=[airport.latitude, airport.longitude], popup=f"<b>{airport.code}</b><br>{airport.city}, {airport.country}", tooltip=airport.name, icon= folium.Icon(color="red", icon="plane", prefix="fa")).add_to(m)

        if path_airports and len(path_airports) > 1:
            coords = [(a.latitude, a.longitude) for a in path_airports]
            folium.PolyLine(locations=coords, color="red", weight=3, opacity=0.9).add_to(m)

        m.save(output_path)
        return output_path
