from graph.graph import Graph

class GraphController:
    def __init__(self, graph):
        self.graph = graph
    
    def load_data(self, csv_path):
        self.graph.load_from_csv(csv_path)
    
    def check_connectivity(self):
        return self.graph.is_connected()
    
    def get_mst_weight(self):
        result = self.graph.kruskal()
        total = sum(item["Total weight"] for item in result)
        return total
    
    def search_airport(self, code):
        cod = code.strip().upper()
        for airport in self.graph.nodes:
            if airport.code == code:
                return airport
        return None
    
    def farthest_airports(self, code):
        return self.graph.far_airports(code)
    
    def shortest_path(self, code1, code2):
        return self.graph.shortest_path(code1, code2)