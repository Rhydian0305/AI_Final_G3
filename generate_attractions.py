import osmnx as ox

# 抓取所有 amenity 或 tourism 地點：例如 museum、viewpoint、hotel
tags = {
    "tourism": ["museum", "viewpoint", "zoo", "attraction"]  # 不包含 hotel
}

gdf = ox.features_from_place("Taipei, Taiwan", tags=tags)


# 篩出需要的欄位
df = gdf[["name", "tourism", "geometry"]].dropna(subset=["name", "geometry"])

# 拆出經緯度
df["latitude"] = df.geometry.centroid.y
df["longitude"] = df.geometry.centroid.x

# 存成 CSV
df.to_csv("taipei_attractions.csv", index=False)
