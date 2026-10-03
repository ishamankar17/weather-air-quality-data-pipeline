import json
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# Paths

INPUT_FILE = Path(
    r"C:\weather_pipeline_output\processed_weather_air_quality.json"
)

PROJECT_ROOT = Path(
    r"C:\Users\Isha\OneDrive\Desktop\weather-air-quality-data-pipeline"
)

OUTPUT_DIR = PROJECT_ROOT / "visualizations"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Load data

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    data = json.load(file)

df = pd.DataFrame(data)


# Prepare data

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    errors="coerce"
)

df["european_aqi"] = pd.to_numeric(
    df["european_aqi"],
    errors="coerce"
)

# Extract hour from timestamp
df["hour"] = df["timestamp"].dt.hour

# Remove records where AQI is missing
aqi_df = df.dropna(
    subset=["hour", "european_aqi"]
).copy()

# Calculate average AQI for each hour

hourly_aqi = (
    aqi_df
    .groupby("hour", as_index=False)["european_aqi"]
    .mean()
)

hourly_aqi["european_aqi"] = hourly_aqi[
    "european_aqi"
].round(2)



# Create visualization

fig, ax = plt.subplots(figsize=(10, 5))

ax.plot(
    hourly_aqi["hour"],
    hourly_aqi["european_aqi"],
    marker="o",
    linewidth=1.8
)

ax.set_title(
    "Average European AQI by Hour"
)

ax.set_xlabel(
    "Hour of Day"
)

ax.set_ylabel(
    "Average European AQI"
)

# Show all 24 hours on the x-axis
ax.set_xticks(range(24))

ax.grid(
    True,
    alpha=0.3
)


# Highlight highest average AQI hour

peak_index = hourly_aqi[
    "european_aqi"
].idxmax()

peak_hour = hourly_aqi.loc[
    peak_index,
    "hour"
]

peak_aqi = hourly_aqi.loc[
    peak_index,
    "european_aqi"
]

ax.scatter(
    peak_hour,
    peak_aqi,
    s=60,
    zorder=3
)

ax.annotate(
    f"Peak: {peak_aqi:.2f} AQI\n"
    f"Hour: {peak_hour:02d}:00",
    xy=(peak_hour, peak_aqi),
    xytext=(0, 25),
    textcoords="offset points",
    ha="center",
    va="bottom",
    bbox=dict(
        boxstyle="round,pad=0.3",
        facecolor="white",
        edgecolor="gray",
        alpha=0.9
    ),
    arrowprops=dict(
        arrowstyle="->",
        connectionstyle="arc3,rad=0"
    )
)

# Save chart

output_file = OUTPUT_DIR / "hourly_aqi_pattern.png"

fig.tight_layout()

fig.savefig(
    output_file,
    dpi=150,
    bbox_inches="tight"
)

plt.close(fig)


# Print results

print("Hourly AQI analysis completed.")
print(f"Peak average AQI: {peak_aqi:.2f} at {peak_hour:02d}:00")
print(f"Chart saved to: {output_file}")

# 6. Daily Summary

daily_summary = (
    df.dropna(subset=["timestamp"])
    .assign(date=df["timestamp"].dt.date)
    .groupby("date", as_index=False)
    .agg(
        avg_temperature_c=("temperature_c", "mean"),
        avg_pm2_5=("pm2_5", "mean"),
        avg_aqi=("european_aqi", "mean")
    )
)

daily_summary["avg_temperature_c"] = (
    daily_summary["avg_temperature_c"].round(2)
)

daily_summary["avg_pm2_5"] = (
    daily_summary["avg_pm2_5"].round(2)
)

daily_summary["avg_aqi"] = (
    daily_summary["avg_aqi"].round(2)
)


fig, axes = plt.subplots(
    2,
    1,
    figsize=(12, 8),
    sharex=True
)

# Average Temperature
axes[0].plot(
    daily_summary["date"],
    daily_summary["avg_temperature_c"],
    marker="o",
    linewidth=1.8
)

axes[0].set_title(
    "Average Daily Temperature"
)

axes[0].set_ylabel(
    "Temperature (°C)"
)

axes[0].grid(
    True,
    alpha=0.3
)


# Average PM2.5 and AQI
axes[1].plot(
    daily_summary["date"],
    daily_summary["avg_pm2_5"],
    marker="o",
    linewidth=1.8,
    label="PM2.5"
)

axes[1].plot(
    daily_summary["date"],
    daily_summary["avg_aqi"],
    marker="o",
    linewidth=1.8,
    label="AQI"
)

axes[1].set_title(
    "Daily Average PM2.5 and AQI"
)

axes[1].set_xlabel(
    "Date"
)

axes[1].set_ylabel(
    "Value"
)

axes[1].grid(
    True,
    alpha=0.3
)

axes[1].legend()

fig.suptitle(
    "Daily Weather and Air Quality Summary",
    fontsize=15
)

fig.tight_layout(pad=2.0)

output_file = OUTPUT_DIR / "daily_summary.png"

fig.savefig(
    output_file,
    dpi=150,
    bbox_inches="tight"
)

plt.close(fig)

print(f"Created: {output_file}")