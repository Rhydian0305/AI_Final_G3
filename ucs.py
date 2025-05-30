import csv
import heapq
from collections import defaultdict

def load_graph(csv_path):
    graph = defaultdict(list)
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            u = int(row['start'])
            v = int(row['end'])
            dist = float(row['distance'])
            graph[u].append((v, dist))
    return graph

def ucs(graph, start, end):
    import heapq
    from collections import defaultdict

    pq = [(0, start, [start])]
    visited = set()
    num_visited = 0

    while pq:
        cost, node, path = heapq.heappop(pq)
        if node not in visited:
            visited.add(node)
            num_visited += 1

            if node == end:
                return path, cost, num_visited

            for neighbor, weight in graph[node]:
                if neighbor not in visited:
                    heapq.heappush(pq, (cost + weight, neighbor, path + [neighbor]))

    return [], 0, num_visited


if __name__ == "__main__":
    graph = load_graph("edges.csv")
    start = 25423587
    end = 618955584  # 隨便選一組在你的資料裡存在的
    path, dist, visited = ucs(start, end, graph)
    print("✅ 路徑節點數：", len(path))
    print("📏 總距離：", dist)
    print("🔍 拜訪節點數：", visited)
