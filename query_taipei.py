from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd

# 你的金鑰檔案名稱
KEY_PATH = "precise-works-461407-i9-392ba2ddc305.json"

# 你的 GCP 專案 ID
PROJECT_ID = "precise-works-461407-i9"

# 指定 EU 區域以避免找不到資料表錯誤
credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
client = bigquery.Client(
    credentials=credentials,
    project=PROJECT_ID,
    location="EU"  # ← ← ← 一定要有這行，否則會查不到表
)

# 查詢台北市景點（tourism 類型）
query = """
SELECT 
  t.value AS name,
  t.key AS tag_type,
  ST_Y(n.geometry) AS latitude,
  ST_X(n.geometry) AS longitude
FROM 
  FROM `precise-works-461407-i9.my_osm.planet_node_tags` n
JOIN 
  `bigquery-public-data.geo_openstreetmap.planet_node_tags` t
ON n.id = t.node_id
WHERE 
  t.key = "tourism"
  AND ST_WITHIN(
    n.geometry,
    ST_GEOGFROMTEXT("POLYGON((121.45 24.95, 121.45 25.2, 121.65 25.2, 121.65 24.95, 121.45 24.95))")
  )
LIMIT 200
"""

df = client.query(query).to_dataframe()
df.to_csv("taipei_tourism.csv", index=False)
print("已成功查詢並輸出 taipei_tourism.csv")
