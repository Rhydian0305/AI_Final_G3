import pickle
import pandas as pd
import os
import ast

# 對齊所有可能的景點類型欄位
ALL_TOURISM_TYPES = [
    "viewpoint", "attraction", "museum", "artwork", "theme_park", "zoo"
]

def predict_best_route(user_id, alpha, gamma, candidate_paths, candidate_costs, tourism_weights={}):
    model_path = f"models/model_{user_id}.pkl"
    if not os.path.exists(model_path):
        print("⚠️ 無個人模型，使用預設規則選擇最短成本路線")
        return candidate_costs.index(min(candidate_costs))

    with open(model_path, "rb") as f:
        model = pickle.load(f)

    tourism_vector = [tourism_weights.get(key, 0.0) for key in ALL_TOURISM_TYPES]

    X_pred = pd.DataFrame([
        {
            "alpha": alpha,
            "gamma": gamma,
            "total_cost": cost,
            "num_nodes": len(path),
            "duration": cost / 70,
            **{f"tw_{key}": tourism_weights.get(key, 0.0) for key in ALL_TOURISM_TYPES}
        }
        for path, cost in zip(candidate_paths, candidate_costs)
    ])

    predicted_scores = model.predict(X_pred)
    return predicted_scores.argmax()

