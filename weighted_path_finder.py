import pandas as pd
import networkx as nx
import osmnx as ox
import pickle
from difflib import get_close_matches
import folium
import webbrowser
from itertools import islice
from datetime import datetime
from collections import defaultdict
from math import radians, cos, sin, asin, sqrt
import heapq
import csv
import os
from ast import literal_eval

# ✅ 匯入個人化推薦模組
from ml_predictor import predict_best_route

# ===== 參數學習：自動平均過去紀錄偏好 =====
def learn_user_preferences(log_file='user_logs.csv'):
    if not os.path.exists(log_file):
        return 1.0, 1.0, 0.0
    df_log = pd.read_csv(log_file)
    return df_log["alpha"].mean(), df_log["beta"].mean(), df_log["gamma"].mean()

# ===== 使用者輸入偏好參數與 ID =====
user_id = input("請輸入你的使用者代號：")
use_auto = input("是否根據過去偏好自動設定係數？(y/n): ").strip().lower()
if use_auto == 'y':
    alpha, beta, gamma = learn_user_preferences()
    print(f"套用偏好：alpha={alpha:.2f}, beta={beta:.2f}, gamma={gamma:.2f}")
else:
    alpha = float(input("請輸入 speed camera 懲罰係數 alpha（建議值 0~2，例如 0.8）："))
    beta = float(input("請輸入 bike_unable 懲罰係數 beta（建議值 0~3，例如 1.5）："))
    gamma = float(input("請輸入 scenic_score 加分係數 gamma（建議值 0~1，例如 0.3）："))

# ===== 載入圖資料 =====
df = pd.read_csv("edges.csv")
places_df = pd.read_csv("taipei_attractions.csv")
place_names = places_df["name"].dropna().tolist()

for col in ["has_camera", "bike_unable", "scenic_score"]:
    if col not in df.columns:
        df[col] = 0

df["has_camera"] = df["has_camera"].astype(int)
df["bike_unable"] = df["bike_unable"].astype(int)
df["weighted_cost"] = df["distance"] * (
    1 + alpha * df["has_camera"] + beta * df["bike_unable"] - gamma * df["scenic_score"]
)
df["weighted_cost"] = df["weighted_cost"].clip(lower=0.01)

# ===== 地點處理 =====
def resolve_place_input(prompt):
    name = input(prompt)
    if name in place_names:
        return name
    matches = get_close_matches(name, place_names, n=3, cutoff=0.5)
    if matches:
        print("⚠️ 找不到完全相符的地名，你可能想找：")
        for i, m in enumerate(matches):
            print(f"  {i+1}. {m}")
        choice = input("請選擇 1~3 中的一個，請按enter繼續：")
        if choice.isdigit() and 1 <= int(choice) <= len(matches):
            return matches[int(choice)-1]
        else:
            return resolve_place_input(prompt)
    else:
        print("❌ 沒有找到類似地名，請再試一次")
        return resolve_place_input(prompt)

source_name = resolve_place_input("請輸入起點地名（例如：台北車站）：")
target_name = resolve_place_input("請輸入終點地名（例如：台北101）：")
source_point = ox.geocoder.geocode(source_name)
target_point = ox.geocoder.geocode(target_name)

# ===== 建圖與座標 =====
G_osm = ox.graph_from_place("Taipei, Taiwan", network_type='walk')
source = ox.distance.nearest_nodes(G_osm, source_point[1], source_point[0])
target = ox.distance.nearest_nodes(G_osm, target_point[1], target_point[0])
custom_graph = defaultdict(list)
for _, row in df.iterrows():
    u, v = int(row['start']), int(row['end'])
    cost = float(row.get('weighted_cost', row['distance']))
    custom_graph[u].append((v, cost))

nxG = nx.DiGraph()
for u in custom_graph:
    for v, c in custom_graph[u]:
        nxG.add_edge(u, v, weight=c)

coords = {n: (G_osm.nodes[n]['y'], G_osm.nodes[n]['x']) for n in G_osm.nodes}

# ===== K條候選路徑 =====
def k_shortest_paths(G, source, target, k=3):
    return list(islice(nx.shortest_simple_paths(G, source, target, weight='weight'), k))

candidate_paths = k_shortest_paths(nxG, source, target, k=3)
candidate_costs = [sum(nxG[u][v]['weight'] for u, v in zip(p[:-1], p[1:])) for p in candidate_paths]

# ===== 使用個人模型推薦最適路徑 =====
recommended_idx = predict_best_route(user_id, alpha, beta, gamma, candidate_paths, candidate_costs)
shortest_path = candidate_paths[recommended_idx]
total_cost = candidate_costs[recommended_idx]

# ===== 畫圖並顯示 =====
coords_list = [(G_osm.nodes[n]['y'], G_osm.nodes[n]['x']) for n in shortest_path if n in G_osm.nodes]
m = folium.Map(location=coords_list[0], zoom_start=14)
folium.PolyLine(coords_list, color='blue', weight=5, tooltip="推薦路線").add_to(m)
folium.Marker(coords_list[0], popup="起點", icon=folium.Icon(color='green')).add_to(m)
folium.Marker(coords_list[-1], popup="終點", icon=folium.Icon(color='red')).add_to(m)
m.save("route_map.html")
webbrowser.open_new_tab(os.path.abspath("route_map.html"))
print("✅ 地圖已儲存並打開 route_map.html")

# ===== 使用者回饋紀錄 =====
def log_user_choice(filename, user_id, source, target, alpha, beta, gamma, path, cost, feedback, duration):
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            user_id,
            source,
            target,
            alpha,
            beta,
            gamma,
            path,
            cost,
            feedback,
            duration
        ])

feedback = int(input("請對這條路線評分 (1-5)："))
duration = float(input("請輸入實際所花時間（分鐘）："))
log_user_choice(
    "user_logs.csv", user_id, source_name, target_name,
    alpha, beta, gamma, shortest_path, total_cost,
    feedback, duration
)

print("✅ 已記錄使用者回饋與偏好")
