import osmnx as ox
import pickle

print("正在下載台北市路網...")
G = ox.graph_from_place("Taipei, Taiwan", network_type='walk')

print("📐 正在轉換為 geometry...")
custom_edges = []

for u, v, k, data in G.edges(keys=True, data=True):
    if 'geometry' in data:
        coords = list(data['geometry'].coords)
    else:
        coords = [
            (G.nodes[u]['y'], G.nodes[u]['x']),
            (G.nodes[v]['y'], G.nodes[v]['x'])
        ]

    # 原向邊
    custom_edges.append({
        "u": u,
        "v": v,
        "geometry": coords,
        "distance": data.get("length", 1)
    })

    # 反向邊（加 reversed()）
    custom_edges.append({
        "u": v,
        "v": u,
        "geometry": list(reversed(coords)),
        "distance": data.get("length", 1)
    })

# 儲存成 graph.pkl
with open("graph.pkl", "wb") as f:
    pickle.dump(custom_edges, f)

print("已成功產生 graph.pkl，可用於地圖與路線搜尋")
