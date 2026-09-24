import json
from collections import Counter

path = r"ai_service\data\Road data.geojson"

print("Loading:", path)

with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

features = data.get("features", [])

print("\nTOTAL FEATURES:", len(features))

geometry_counts = Counter()
highway_counts = Counter()

line_features = 0
road_features = 0

for feature in features:
    geometry = feature.get("geometry") or {}
    geom_type = geometry.get("type")

    geometry_counts[geom_type] += 1

    props = feature.get("properties") or {}

    highway = props.get("highway")

    if highway is not None:
        highway_counts[str(highway)] += 1

    if geom_type in ("LineString", "MultiLineString"):
        line_features += 1

    if highway is not None:
        road_features += 1

print("\nGEOMETRY TYPES:")
for k, v in geometry_counts.items():
    print(f"  {k}: {v}")

print("\nFEATURES WITH HIGHWAY PROPERTY:")
print(" ", road_features)

print("\nLINE FEATURES:")
print(" ", line_features)

print("\nHIGHWAY TYPES:")
for k, v in highway_counts.most_common():
    print(f"  {k}: {v}")