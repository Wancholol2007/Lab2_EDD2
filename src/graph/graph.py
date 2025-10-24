from collections import defaultdict, deque
from math import radians, sin, cos, sqrt, atan2
import csv

from numpy import stack
from graph.airport import Airport
import os

class Graph:
    def __init__(self):
        self.vertices = {}
        self.adj_list = defaultdict(list)
    
    def add_airport(self, airport: Airport):
        if airport.code not in self.vertices:
            self.vertices[airport.code] = airport

    def add_route(self, code1:str, code2: str, weight: float):
        if code1 in self.vertices and code2 in self.vertices:
            if not any(v == code2 for v, _ in self.adj_list[code1]):
                self.adj_list[code1].append((code2, weight))
                self.adj_list[code2].append((code1, weight))
    
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        R = 6371.0
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        dis = 2 * R * atan2(sqrt(a), sqrt(1 - a))
        return dis
    
    def load_from_csv(self, filename: str):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.abspath(os.path.join(current_dir, ".."))
        dataset_path = os.path.join(src_dir, "dataset", filename)

        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"No se encontró el archivo CSV en: {dataset_path}")

        print(f"[INFO] Cargando datos desde: {dataset_path}")

        with open(dataset_path, encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                src = Airport(row['Source Airport Code'], row['Source Airport Name'], row['Source Airport City'], row['Source Airport Country'], float(row['Source Airport Latitude']), float(row['Source Airport Longitude']))
                dst = Airport(row['Destination Airport Code'], row['Destination Airport Name'], row['Destination Airport City'], row['Destination Airport Country'], float(row['Destination Airport Latitude']), float(row['Destination Airport Longitude']))
                self.add_airport(src)
                self.add_airport(dst)
                distance = self.haversine_distance(src.latitude, src.longitude, dst.latitude, dst.longitude)
                self.add_route(src.code, dst.code, distance)

        return self

    def bfs(self, start_code, visited):
        q = deque([start_code])
        component = []
        visited.add(start_code)

        while q:
            current = q.popleft()
            component.append(current)
            for neighbor, _ in self.adj_list[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    q.append(neighbor)
        
        return component
    
    def get_connected_components(self):
        visited = set()
        components = []
        for code in self.vertices:
            if code not in visited:
                comp = self.bfs(code, visited)
                components.append(comp)
        
        return components
    
    def components_summary(self):
        comps = self.get_connected_components()
        summary = []
        for i, comp in enumerate(comps, start=1):
            summary.append({
                "id": i,
                "size": len(comp),
                "nodes": sorted(comp)
            })
        return summary
    
    def is_connected(self):
        if not self.vertices:
            return False
        visited = set()
        start = next(iter(self.vertices))
        stack = [start]

        while stack:
            u = stack.pop()
            if u in visited:
                continue
            visited.add(u)
            
            for v, _ in self.adj_list.get(u, []):
                if v not in visited:
                    stack.append(v)

        return len(visited) == len(self.vertices)


    
    def kruskal(self):
        edges = []
        seen = set()

        for u in self.vertices:
            for v, weight in self.adj_list[u]:
                edge_key = tuple(sorted([u, v]))
                if edge_key not in seen:
                    seen.add(edge_key)
                    edges.append((weight, u, v))

        edges.sort()
        parent = {}
        rank = {}

        def find(u):
            if parent[u] != u:
                parent[u] = find(parent[u])
            return parent[u]
        
        def union(u, v):
            root_u = find(u)
            root_v = find(v)
            if root_u != root_v:
                if rank[root_u] < rank[root_v]:
                    parent[root_u] = root_v
                else:
                    parent[root_v] = root_u
                    if rank[root_u] == rank[root_v]:
                        rank[root_u] += 1

        for vertex in self.vertices:
            parent[vertex] = vertex
            rank[vertex] = 0

        mst_weight = 0
        mst_edges = []
        for weight, u, v in edges:
            if find(u) != find(v):
                union(u, v)
                mst_edges.append((u, v, weight))
                mst_weight += weight

        return mst_edges, mst_weight
    
    def kruskal_por_componentes(self):
        components = self.get_connected_components()
        results = []

        for i, component in enumerate(components, start=1):
            subgraph = Graph()
            for vertex in component:
                subgraph.add_airport(self.vertices[vertex])

            for u in component:
                for v, weight in self.adj_list[u]:
                    if v in component:
                        subgraph.add_route(u, v, weight)

            mst_edges, mst_weight = subgraph.kruskal()

            results.append({"Componente":i, "Rutas":mst_edges, "Peso total":mst_weight})

        return results
        
    def dijkstra(self, start_code: str):
        if start_code not in self.vertices:
            raise ValueError(f"El aeropuerto {start_code} no existe en el grafo")
        
        dist = {code: float('inf') for code in self.vertices}
        prev = {code: None for code in self.vertices}
        dist[start_code] = 0
        unvisited = set(self.vertices.keys())

        while unvisited:
            current = min(unvisited, key = lambda node: dist[node])

            if dist[current] == float ('inf'):
                break
            unvisited.remove(current)

            for neighbor, weight in self.adj_list[current]:
                if neighbor in unvisited:
                    alt = dist[current] + weight
                    if alt < dist[neighbor]:
                        dist[neighbor] = alt
                        prev[neighbor] = current
                    
        return dist, prev
    
    def far_airports(self, start_code: str):
        if start_code not in self.vertices:
            raise ValueError(f"El aeropuerto {start_code} no existe en el grafo")
        
        dist, _ = self.dijkstra(start_code)
        airports = [(code, d) for code, d in dist.items() if d != float('inf') and code != start_code]
        airports.sort(key = lambda x: x[1], reverse = True)
        far_airports = airports[:10]
        result = [(self.vertices[code], distance) for code, distance in far_airports]
        
        return result
    
    def shortest_path(self, start_code: str, end_code: str):
        if start_code not in self.vertices or end_code not in self.vertices:
            return None, float('inf')
        
        unvisited = set(self.vertices.keys())
        distances = {code: float('inf') for code in self.vertices}
        previous = {code: None for code in self.vertices}
        distances[start_code] = 0

        while unvisited:
            current = None
            current_dist = float('inf')
            for code in unvisited:
                if distances[code] < current_dist:
                    current = code
                    current_dist = distances[code]
            
            if current is None or current == end_code:
                break

            unvisited.remove(current)

            for neighbor, weight in self.adj_list[current]:
                if neighbor in unvisited:
                    new_dist = distances[current] + weight
                    if new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist
                        previous[neighbor] = current
        
        if distances[end_code] == float('inf'):
            return None, float('inf')
        
        path_codes = []
        current = end_code
        while current is not None:
            path_codes.insert(0, current)
            current = previous[current]

        path_airports = [self.vertices[code] for code in path_codes]
        return path_airports, distances[end_code]

    def __len__(self):
        return len(self.vertices)
    
    def __str__(self):
        return f"Graph(vertices={len(self.vertices)}, edges={sum(len(v) for v in self.adj_list.values()) // 2})"
    
