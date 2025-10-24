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
        import folium
        from folium.plugins import MarkerCluster
        import os

        base_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.abspath(os.path.join(base_dir, ".."))
        output_dir = os.path.join(src_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        map_path = os.path.join(output_dir, "map.html")

        if not self.graph.vertices:
            print("[ERROR] No hay aeropuertos cargados.")
            return None

        latitudes = [a.latitude for a in self.graph.vertices.values()]
        longitudes = [a.longitude for a in self.graph.vertices.values()]
        center_lat = sum(latitudes) / len(latitudes)
        center_lon = sum(longitudes) / len(longitudes)

        m = folium.Map(location=[center_lat, center_lon], zoom_start=3)

        cluster = MarkerCluster().add_to(m)

        for airport in self.graph.vertices.values():
            folium.Marker(
                location=[airport.latitude, airport.longitude],
                popup=f"<b>{airport.code}</b><br>{airport.city}, {airport.country}",
                tooltip=airport.name,
                icon=folium.Icon(color="blue", icon="plane", prefix="fa")
            ).add_to(cluster)

        m.save(map_path)
        print(f"[INFO] Mapa inicial generado con agrupación en: {map_path}")
        return map_path
    
    def highlight_airport(self, airport_code):
        import folium
        from folium import Map, Marker
        from folium.plugins import MarkerCluster
        import os

        airports = list(self.graph.vertices.values())
        map_center = [airports[0].latitude, airports[0].longitude] if airports else [0, 0]
        m = Map(location=map_center, zoom_start=3)
        cluster = MarkerCluster().add_to(m)

        for airport in airports:
            color = "red" if airport.code == airport_code else "blue"
            Marker(
                location=[airport.latitude, airport.longitude],
                popup=f"{airport.code} - {airport.name}",
                icon=folium.Icon(color=color)
            ).add_to(cluster)

        output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))
        os.makedirs(output_dir, exist_ok=True)
        map_path = os.path.join(output_dir, "map.html")
        m.save(map_path)
        return map_path

    def show_farthest_airports(self, origin_code):
        import folium
        from folium import Map, Marker
        from folium.plugins import MarkerCluster
        import os

        farthest = self.graph.far_airports(origin_code)
        origin = self.graph.vertices.get(origin_code)
        if not origin or not farthest:
            return None

        m = Map(location=[origin.latitude, origin.longitude], zoom_start=3)
        cluster = MarkerCluster().add_to(m)

        Marker(
            location=[origin.latitude, origin.longitude],
            popup=f"Origen: {origin.code} - {origin.name}",
            icon=folium.Icon(color="red", icon="home")
        ).add_to(cluster)

        for airport, dist in farthest:
            Marker(
                location=[airport.latitude, airport.longitude],
                popup=f"{airport.code} - {airport.name} ({dist:.2f} km)",
                icon=folium.Icon(color="green", icon="plane")
            ).add_to(cluster)

        output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))
        os.makedirs(output_dir, exist_ok=True)
        map_path = os.path.join(output_dir, "map.html")
        m.save(map_path)
        return map_path

    def show_shortest_path(self, path):
        import folium
        from folium import Map, Marker, PolyLine
        from folium.plugins import MarkerCluster
        import os

        if not path or len(path) < 2:
            return None

        start = path[0]
        end = path[-1]
        middle = path[1:-1]

        m = Map(location=[start.latitude, start.longitude], zoom_start=4)
        cluster = MarkerCluster().add_to(m)

        Marker(
            location=[start.latitude, start.longitude],
            popup=f"Origen: {start.code} - {start.name}",
            icon=folium.Icon(color="red", icon="home")
        ).add_to(cluster)

        for airport in middle:
            Marker(
                location=[airport.latitude, airport.longitude],
                popup=f"Escala: {airport.code} - {airport.name}",
                icon=folium.Icon(color="green", icon="plane")
            ).add_to(cluster)

        Marker(
            location=[end.latitude, end.longitude],
            popup=f"Destino: {end.code} - {end.name}",
            icon=folium.Icon(color="red", icon="flag")
        ).add_to(cluster)

        coords = [[a.latitude, a.longitude] for a in path]
        PolyLine(coords, color="blue", weight=3, opacity=0.8).add_to(m)

        output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))
        os.makedirs(output_dir, exist_ok=True)
        map_path = os.path.join(output_dir, "map.html")
        m.save(map_path)
        return map_path
