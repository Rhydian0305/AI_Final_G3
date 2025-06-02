# 根據格式模擬生成 user_logs.csv
import pandas as pd
import random  
import numpy as np
def generate_realistic_logs(n_per_user=100):
    users = {
        "Tony": {"alpha": 2.0, "beta": 0.0, "gamma": 1.0},   # 喜歡公園安靜（景色高 gamma）
        "Mary": {"alpha": 0.5, "beta": 0.0, "gamma": 1.0},   # 喜歡風景漂亮（景色高 gamma）
        "David": {"alpha": 2.0, "beta": 1.0, "gamma": 0.0},  # 討厭市區（camera 多 → alpha 高）
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
                params["alpha"], params["beta"], params["gamma"],
                path, cost, feedback, duration
            ])

    return pd.DataFrame(records, columns=[
        "user_id", "source_name", "target_name", "alpha", "beta", "gamma",
        "chosen_path", "total_cost", "feedback", "duration"
    ])

df_simulated = generate_realistic_logs()
print(df_simulated.head())  # 顯示驗證內容
df_simulated.to_csv("user_logs.csv", index=False)
print("user_logs_simulated.csv 已成功產生！")