import osmnx as ox
import pickle

# 抓取台北市的街道網路（以行人路網為例）
print("📦 正在下載台北市路網...")
G = ox.graph_from_place("Taipei, Taiwan", network_type='walk')

# 將資料轉換成 GeoDataFrame（取得每條邊的幾何座標與距離）
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
    custom_edges.append({
        "u": u,
        "v": v,
        "geometry": coords,
        "distance": data.get("length", 1)
    })

# 儲存為 .pkl 檔
with open("graph.pkl", "wb") as f:
    pickle.dump(custom_edges, f)

print("✅ 已成功產生 graph.pkl，可用於地圖與路線搜尋")
