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
from scipy.spatial import KDTree

from ml_predictor import predict_best_route

ALL_TOURISM_TYPES = ["viewpoint", "attraction", "museum", "artwork", "theme_park", "zoo"]

# ===== 使用者偏好學習（限定使用者） =====
def learn_user_preferences(user_id, log_file='user_logs.csv'):
    if not os.path.exists(log_file):
        return 1.0, 0.0, {}
    df_log = pd.read_csv(log_file)
    df_user = df_log[df_log["user_id"] == user_id]
    if df_user.empty:
        return 1.0, 0.0, {}
    try:
        tourism_weights = literal_eval(df_user["tourism_weights"].dropna().iloc[-1])
    except:
        tourism_weights = {}
    return df_user["alpha"].mean(), df_user["gamma"].mean(), tourism_weights

# ===== 使用者輸入偏好參數與 ID =====
user_id = input("請輸入你的使用者代號：")
use_auto = input("是否根據過去偏好自動設定係數？(y/n): ").strip().lower()
if use_auto == 'y':
    alpha, gamma, tourism_weights = learn_user_preferences(user_id)
    print(f"套用偏好：alpha={alpha:.2f}, gamma={gamma:.2f}, tourism_weights={tourism_weights}")
else:
    alpha = float(input("請輸入 speed camera 懲罰係數 alpha（建議值 0~2，例如 0.8）："))
    gamma = float(input("請輸入 scenic_score 加分係數 gamma（建議值 0~1，例如 0.3）："))
    print("請輸入你偏好的景點類型權重，例如 viewpoint:1.0 attraction:0.5 museum:0")
    tourism_weights_input = input("輸入格式為 類型:分數，以空格分隔：")
    tourism_weights = {}
    for item in tourism_weights_input.split():
        if ":" in item:
            key, val = item.split(":")
            try:
                tourism_weights[key.strip()] = float(val)
            except:
                pass

# ===== 載入圖資料 =====
df = pd.read_csv("edges.csv")
places_df = pd.read_csv("taipei_attractions.csv")
place_names = places_df["name"].dropna().tolist()

for col in ["has_camera", "scenic_score", "scenic_view", "scenic_park"]:
    if col not in df.columns:
        df[col] = 0

places_df["score"] = places_df["tourism"].map(tourism_weights).fillna(0)
points = places_df[["latitude", "longitude"]].dropna().values
scores = places_df["score"].dropna().values
scenic_tree = KDTree(points)
radius = 50 / 111000
scenic_scores = []
for _, row in df.iterrows():
    mid_lat = (row.get("lat1", 0) + row.get("lat2", 0)) / 2
    mid_lon = (row.get("lon1", 0) + row.get("lon2", 0)) / 2
    idxs = scenic_tree.query_ball_point([mid_lat, mid_lon], r=radius)
    scenic_scores.append(sum(scores[i] for i in idxs))

df["scenic_score"] = scenic_scores

df["has_camera"] = df["has_camera"].astype(int)
df["weighted_cost"] = df["distance"] * (
    1 + (alpha * df["has_camera"]) ** 2 - gamma * df["scenic_score"]
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

source_name = resolve_place_input("請輸入起點地名（例如：臺北車站）：")
target_name = resolve_place_input("請輸入終點地名（例如：臺北101）：")
source_point = ox.geocoder.geocode(source_name)
target_point = ox.geocoder.geocode(target_name)

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
recommended_idx = predict_best_route(user_id, alpha, gamma, candidate_paths, candidate_costs, tourism_weights)
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
def log_user_choice(filename, user_id, source, target, alpha, gamma, path, cost, feedback, duration, tourism_weights):
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            user_id,
            source,
            target,
            alpha,
            gamma,
            path,
            cost,
            feedback,
            duration,
            tourism_weights
        ])

feedback = int(input("請對這條路線評分 (1-5)："))
duration = float(input("請輸入實際所花時間（分鐘）："))
log_user_choice(
    "user_logs.csv", user_id, source_name, target_name,
    alpha, gamma, shortest_path, total_cost,
    feedback, duration, tourism_weights
)

print("✅ 已記錄使用者回饋與偏好")
