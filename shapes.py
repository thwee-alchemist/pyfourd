class Tetrahedron:
    def __init__(self, fourd, vertex_id, edge_id):
        self.fourd = fourd
        start = vertex_id

        fourd.graph.add_vertex(vertex_id, color="darkblue")
        vertex_id += 1

        fourd.graph.add_vertex(vertex_id, color="darkorange")
        vertex_id += 1

        fourd.graph.add_vertex(vertex_id, color="darkblue")
        vertex_id += 1

        fourd.graph.add_vertex(vertex_id, color="darkorange")
        vertex_id += 1

        edge_start = edge_id
        fourd.graph.add_edge(edge_start + 0, start + 0, start + 1, color="black")
        fourd.graph.add_edge(edge_start + 1, start + 2, start + 3, color="black")
        fourd.graph.add_edge(edge_start + 2, start + 1, start + 2, color="black")
        fourd.graph.add_edge(edge_start + 3, start + 0, start + 2, color="black")
        fourd.graph.add_edge(edge_start + 4, start + 1, start + 3, color="black")
        fourd.graph.add_edge(edge_start + 5, start + 0, start + 3, color="black")
        edge_id += 6
        
        self.graph = [[start, vertex_id], [edge_start, edge_id]]


