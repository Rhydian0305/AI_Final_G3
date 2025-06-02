import pickle
import pandas as pd

# 載入你剛剛用 osmnx 產生的 graph.pkl
with open("graph.pkl", "rb") as f:
    graph = pickle.load(f)

# 擷取起點、終點與距離，並加入反向邊
edges_data = []
for edge in graph:
    u = edge["u"]
    v = edge["v"]
    dist = edge["distance"]

    # 正向邊
    edges_data.append({"start": u, "end": v, "distance": dist})
    # 反向邊（讓圖是雙向）
    edges_data.append({"start": v, "end": u, "distance": dist})

# 存成 CSV 檔
df = pd.DataFrame(edges_data)
df.to_csv("edges.csv", index=False)

print("已產出 edges.csv，格式：start,end,distance（含雙向邊）")
