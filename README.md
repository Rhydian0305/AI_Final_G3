# Personalized Scenic Map Navigation System

A personalized route planning system that allows users to adjust preferences and generates multiple recommended paths using a modified Yen's K Shortest Paths algorithm.

## 📌 Introduction

Traditional navigation tools optimize for shortest distance or fastest time. However, users often prefer routes that are safer, flatter, or more scenic. Our system integrates user-adjustable preferences—such as avoiding steep slopes or promoting scenic landmarks—into a personalized navigation system using a customized cost function and **Yen’s algorithm**, which generates multiple viable routes for flexible comparison.

## 💡 Features

- Avoid undesirable roads (speed camera)
- Prefer routes through scenic areas based on landmarks

## ⚙️ Platform and Dataset

- **Platform**: Python with `networkx`, `folium`, `osmnx`
- **Data**: OpenStreetMap data and user-defined scenic spot CSV

## ▶️ How to Run

1. **Run `main.py`**
   - Displays a list of Taipei attractions for users to choose a starting point and destination

2. **Run `weighted_path_finder.py`**
   - Users can input their identity (currently supported: `David`, `Mary`, `Tony`)
   - The system automatically selects personalized weights and uses Yen’s Algorithm to calculate recommended routes

3. **View Results**
   - The result map will be automatically saved as an HTML file (e.g., `route_map.html`) and can be viewed in any web browser
