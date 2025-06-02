#可刪
import csv
import math
import pickle
from tqdm import tqdm 

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # 地球半徑（公尺）
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# 讀取圖形資料
with open("graph.pkl", "rb") as f:
    edges = pickle.load(f)

# 擷取節點與對應座標
node_coords = {}
for edge in edges:
    u, v = edge["u"], edge["v"]
    if u not in node_coords:
        node_coords[u] = edge["geometry"][0]
    if v not in node_coords:
        node_coords[v] = edge["geometry"][-1]

all_nodes = list(node_coords.keys())

# 寫入標頭
with open("heuristic_values.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["node"] + [str(n) for n in all_nodes])

# 寫入每一列（加上 tqdm 進度條）
with open("heuristic_values.csv", "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for src in tqdm(all_nodes, desc="生成 heuristic 資料"):
        row = [src]
        lat1, lon1 = node_coords[src]
        for dst in all_nodes:
            lat2, lon2 = node_coords[dst]
            dist = haversine(lat1, lon1, lat2, lon2)
            row.append(round(dist, 6))
        writer.writerow(row)
