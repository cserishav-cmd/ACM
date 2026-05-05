import os
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json

# Ensure directories exist
os.makedirs("ui/public/assets/analysis", exist_ok=True)
os.makedirs("src/analysis", exist_ok=True)

def run_analysis():
    print("Loading data...")
    df_path = "models/df.pkl"
    if not os.path.exists(df_path):
        print(f"Error: Dataset not found at {df_path}")
        return

    df = pd.read_pickle(df_path)
    
    # Select relevant columns for agrochemical impact
    cols = ['temp_mean_annual', 'rainfall_annual_mm', 'windspeed_mean', 'yield_kg_per_ha']
    available_cols = [c for c in cols if c in df.columns]
    
    analysis_df = df[available_cols].dropna()
    
    print("Calculating correlations...")
    # Calculate Pearson Correlation
    corr_matrix = analysis_df.corr(method='pearson')
    
    # 1. Visualization: Correlation Heatmap
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
    plt.title("Weather-Agrochemical & Yield Correlation")
    plt.tight_layout()
    plt.savefig("ui/public/assets/analysis/correlation_heatmap.png")
    plt.close()
    
    # 2. Visualization: Scatter Plots for Yield Impact
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    if 'windspeed_mean' in analysis_df.columns:
        sns.regplot(data=analysis_df, x='windspeed_mean', y='yield_kg_per_ha', ax=axes[0], color='blue')
        axes[0].set_title("Impact of Windspeed on Yield\n(Proxy for Drift / Spray Inefficiency)")
        
    if 'rainfall_annual_mm' in analysis_df.columns:
        sns.regplot(data=analysis_df, x='rainfall_annual_mm', y='yield_kg_per_ha', ax=axes[1], color='green')
        axes[1].set_title("Impact of Rainfall on Yield\n(Proxy for Nutrient Leaching)")
        
    if 'temp_mean_annual' in analysis_df.columns:
        sns.regplot(data=analysis_df, x='temp_mean_annual', y='yield_kg_per_ha', ax=axes[2], color='red')
        axes[2].set_title("Impact of Temperature on Yield\n(Proxy for Evaporation/Uptake)")
        
    plt.tight_layout()
    plt.savefig("ui/public/assets/analysis/yield_impact_scatter.png")
    plt.close()

    # Extract Data-Driven Thresholds
    # We will compute basic percentiles to define "extreme" conditions based on the dataset
    insights = {
        "correlations": corr_matrix.to_dict(),
        "thresholds": {}
    }
    
    if 'windspeed_mean' in analysis_df.columns:
        mean_wind = analysis_df['windspeed_mean'].mean()
        p90_wind = analysis_df['windspeed_mean'].quantile(0.90)
        insights['thresholds']['windspeed'] = {
            "moderate": round(mean_wind, 2),
            "unsafe": round(p90_wind, 2)
        }
        
    if 'temp_mean_annual' in analysis_df.columns:
        p85_temp = analysis_df['temp_mean_annual'].quantile(0.85)
        insights['thresholds']['temperature'] = {
            "unsafe": round(p85_temp, 2)
        }
        
    if 'rainfall_annual_mm' in analysis_df.columns:
        p90_rain = analysis_df['rainfall_annual_mm'].quantile(0.90)
        insights['thresholds']['rainfall_annual_unsafe'] = round(p90_rain, 2)

    # Save insights to JSON
    insights_path = "src/analysis/agrochemical_insights.json"
    with open(insights_path, 'w') as f:
        json.dump(insights, f, indent=4)
        
    print(f"Analysis complete. Insights saved to {insights_path}")
    print("Visualizations saved to ui/public/assets/analysis/")

if __name__ == "__main__":
    run_analysis()
