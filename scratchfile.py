import json

with open("config.json") as f:
    config = json.load(f)

total = sum(
    v
    for group in config["sex_age_distribution"].values()
    for v in group.values()
)
print(f"Total: {total}%")