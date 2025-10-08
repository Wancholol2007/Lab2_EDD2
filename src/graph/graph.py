from collections import defaultdict, deque
from math import radians, sin, cos, sqrt, atan2
import csv
from src.graph.airport import Airport

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
    
    def load_from_csv(self, filepath: str):
        with open(filepath, encoding = 'utf-8') as file:
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
    
    def connected_components(self):
        visited = set()
        components = []
        for code in self.vertices:
            if code not in visited:
                comp = self.bfs(code, visited)
                components.append(comp)
        
        return components
    
    def is_connected(self) -> bool:
        return len(self.connected_components()) == 1
    
    def kruskal(self):
        edges = []
        for src in self.adj_list:
            for dest, weight in self. adj_list[src]:
                if (dest, src, weight) not in edges:
                    edges.append((src, dest, weight))

        edges.sort(key = lambda x: x[2])
        
        if self.is_connected():
            print("El grafo es conexo. Calculando MST ... \n")
            ds = DisjointSet(self.vertices.keys())
            mst = []
            total_weight = 0

            for src, dest, weight in edges:
                if ds.find(src) != ds.find(dest):
                    ds.union(src, dest)
                    mst.append((src, dest, weight))
                    total_weight += weight
            
            return [{"Component": list(self.vertices.keys()), "Edges": mst, "Total weight": total_weight}]
        else:
            print("El grafo no es conexo. Calculando MST por componente ...\n")
            components = self.connected_components()
            all_mst = []
            
            for comp in components:
                ds = DisjointSet(comp)
                mst = []
                total_weight = 0
                for src, dest, weight in edges:
                    if src in comp and dest in comp:
                        if ds.find(src) != ds.find(dest):
                            ds.union(src, dest)
                            mst.append((src, dest, weight))
                            total_weight += weight
                all_mst.append({"Component": comp, "Edges": mst, "Total weight": total_weight})
            
            return all_mst
        
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
    

class DisjointSet:
    def __init__(self, vertices):
        self.parent = {v: v for v in vertices}
        self.rank = {v: 0 for v in vertices}

    def find(self, v):
        if self.parent[v] != v:
            self.parent[v] = self.find(self.parent[v])
        return self.parent[v]
    
    def union(self, v1, v2):
        root1 = self.find(v1)
        root2 = self.find(v2)

        if root1 != root2:
            if self.rank[root1] < self.rank[root2]:
                self.parent[root1] = root2
            elif self.rank[root1] > self.rank[root2]:
                self.parent[root2] = root1
            else:
                self.parent[root2] = root1
                self.rank[root1] += 1