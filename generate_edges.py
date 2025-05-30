import pickle
import pandas as pd

# 載入你剛剛用 osmnx 產生的 graph.pkl（必須在同一資料夾）
with open("graph.pkl", "rb") as f:
    graph = pickle.load(f)

# 抓出起點、終點與距離
edges_data = []
for edge in graph:
    edges_data.append({
        "start": edge["u"],
        "end": edge["v"],
        "distance": edge["distance"]
    })

# 存成 CSV 檔
df = pd.DataFrame(edges_data)
df.to_csv("edges.csv", index=False)

print("✅ 已產出 edges.csv，格式：start,end,distance")
