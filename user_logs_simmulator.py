# 根據格式模擬生成 user_logs.csv
import pandas as pd
import random  
import numpy as np

def generate_realistic_logs(n_per_user=100):
    users = {
        "Tony": {
            "alpha": 0.5,
            "gamma": 1.0,
            "tourism_weights": {
                "viewpoint": 0.9,
                "attraction": 0.6,
                "museum": 0.3,
                "theme_park": 0.2,
                "zoo": 0.5
            }
        },
        "Mary": {
            "alpha": 0.3,
            "gamma": 1.0,
            "tourism_weights": {
                "viewpoint": 1.0,
                "attraction": 0.8,
                "artwork": 0.6,
                "museum": 0.2,
                "theme_park": 0.7
            }
        },
        #David喜歡飆車
        "David": {
            "alpha": 2.0,
            "gamma": 0.0,
            "tourism_weights": {
                "viewpoint": 0.0,
                "attraction": 0.0,
                "museum": 0.0
            }
        },
        "Lisa": {
            "alpha": 1.2,
            "gamma": 0.8,
            "tourism_weights": {
                "museum": 1.0,
                "artwork": 0.9,
                "attraction": 0.5,
                "viewpoint": 0.3
            }
        },
        "Eric": {
            "alpha": 0.8,
            "gamma": 0.9,
            "tourism_weights": {
                "zoo": 1.0,
                "theme_park": 0.9,
                "viewpoint": 0.5,
                "attraction": 0.6
            }
        }   
    }

    sample_places = ["台北101", "士林夜市", "南港公園", "寧夏夜市", "青年公園苗圃", "南機場夜市", "觀景台"]
    records = []

    for user, params in users.items():
        for _ in range(n_per_user):
            src, tgt = random.sample(sample_places, 2)
            path = [random.randint(1_000_000_000, 9_999_999_999) for _ in range(random.randint(5, 15))]
            cost = round(random.uniform(3000, 10000), 2)
            duration = round(cost / random.uniform(200, 600), 2)
            feedback = random.choice([5, 4, 3]) if params["gamma"] > 0.8 or params["alpha"] < 1.0 else random.choice([3, 2, 1])
            records.append([
                user, src, tgt,
                params["alpha"], params["gamma"],
                path, cost, feedback, duration,
                str(params["tourism_weights"])
            ])

    return pd.DataFrame(records, columns=[
        "user_id", "source_name", "target_name", "alpha", "gamma",
        "chosen_path", "total_cost", "feedback", "duration", "tourism_weights"
    ])


df_simulated = generate_realistic_logs()
print(df_simulated.head())  # 顯示驗證內容
df_simulated.to_csv("user_logs.csv", index=False)
print("✅ user_logs_simulated.csv 已成功產生！")
