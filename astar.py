import csv
import heapq
from collections import defaultdict
from math import radians, cos, sin, asin, sqrt

def load_graph(edge_file):
    graph = defaultdict(list)
    with open(edge_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            u, v = int(row['start']), int(row['end'])
            dist = float(row['distance'])
            graph[u].append((v, dist))
    return graph

def load_node_coords(coord_file):
    coords = {}
    with open(coord_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            coords[int(row['node'])] = (float(row['lat']), float(row['lon']))
    return coords

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    return R * 2 * asin(sqrt(a))

def astar(start, end, graph, coords):
    pq = [(0 + haversine(*coords[start], *coords[end]), 0, start, [start])]
    visited = set()
    num_visited = 0

    while pq:
        f, g, current, path = heapq.heappop(pq)
        if current in visited:
            continue
        visited.add(current)
        num_visited += 1
        if current == end:
            return path, round(g, 3), num_visited

        for neighbor, dist in graph.get(current, []):
            if neighbor not in visited:
                new_g = g + dist
                h = haversine(*coords[neighbor], *coords[end])
                heapq.heappush(pq, (new_g + h, new_g, neighbor, path + [neighbor]))

    return [], 0, num_visited
