import pickle
import pandas as pd
import os

def predict_best_route(user_id, alpha, beta, gamma, candidate_paths, candidate_costs):
    model_path = f"models/model_{user_id}.pkl"
    if not os.path.exists(model_path):
        print("⚠️ 無個人模型，使用預設規則選擇最短成本路線")
        return candidate_costs.index(min(candidate_costs))

    with open(model_path, "rb") as f:
        model = pickle.load(f)

    X_pred = pd.DataFrame([
        {
            "alpha": alpha,
            "beta": beta,
            "gamma": gamma,
            "total_cost": cost,
            "num_nodes": len(path),
            "duration": cost / 70  # 假設每分鐘走 70 公尺
        }
        for path, cost in zip(candidate_paths, candidate_costs)
    ])

    predicted_scores = model.predict(X_pred)
    return predicted_scores.argmax()
