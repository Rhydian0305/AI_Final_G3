import pandas as pd
import pickle
from ast import literal_eval
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import os
os.makedirs("models", exist_ok=True)


# 讀取並處理資料
df = pd.read_csv("user_logs.csv")
df["chosen_path"] = df["chosen_path"].apply(literal_eval)
df["num_nodes"] = df["chosen_path"].apply(len)
features = ["alpha", "beta", "gamma", "total_cost", "num_nodes", "duration"]

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

print(f"✅ 已完成訓練 {len(user_models)} 個使用者模型")
