import pandas as pd
import pickle
from ast import literal_eval
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import os
os.makedirs("models", exist_ok=True)

# 所有可能出現的景點類型
ALL_TOURISM_TYPES = [
    "viewpoint", "attraction", "museum", "artwork", "theme_park", "zoo"
]

# 讀取並處理資料
df = pd.read_csv("user_logs.csv")
df["chosen_path"] = df["chosen_path"].apply(literal_eval)
df["num_nodes"] = df["chosen_path"].apply(len)

# 將 tourism_weights 欄位轉為多欄 one-hot 欄位（特徵展開）
if "tourism_weights" in df.columns:
    def expand_tourism_weights(val):
        try:
            d = literal_eval(val)
            return [d.get(key, 0.0) for key in ALL_TOURISM_TYPES]
        except:
            return [0.0] * len(ALL_TOURISM_TYPES)

    tourism_expanded = df["tourism_weights"].apply(expand_tourism_weights)
    tourism_df = pd.DataFrame(tourism_expanded.tolist(), columns=[f"tw_{t}" for t in ALL_TOURISM_TYPES])
    df = pd.concat([df, tourism_df], axis=1)

features = ["alpha", "gamma", "total_cost", "num_nodes", "duration"] + [f"tw_{t}" for t in ALL_TOURISM_TYPES if f"tw_{t}" in df.columns]

user_models = {}

for uid, group in df.groupby("user_id"):
    if len(group) < 5:
        continue
    X = group[features]
    y = group["feedback"]
    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)
    user_models[uid] = model
    with open(f"models/model_{uid}.pkl", "wb") as f:
        pickle.dump(model, f)

print(f"已完成訓練 {len(user_models)} 個使用者模型")

