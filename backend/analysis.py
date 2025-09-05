import pandas as pd
import numpy as np

def calculate_efficiency_score(data):
    """
    Calculate composting efficiency score (0-100)
    Based on optimal ranges for each parameter
    """
    score = 0
    
    # C/N Ratio (optimal: 25-30)
    cn_ratio = float(data.get('cn_ratio', 0))
    if 25 <= cn_ratio <= 30:
        score += 20
    elif 20 <= cn_ratio <= 35:
        score += 15
    elif 15 <= cn_ratio <= 40:
        score += 10
    else:
        score += 5
    
    # Moisture Level (optimal: 50-60%)
    moisture = float(data.get('moisture_level', 0))
    if 50 <= moisture <= 60:
        score += 20
    elif 45 <= moisture <= 65:
        score += 15
    elif 40 <= moisture <= 70:
        score += 10
    else:
        score += 5
    
    # Temperature (optimal: 55-65°C)
    temperature = float(data.get('daily_temperature', 0))
    if 55 <= temperature <= 65:
        score += 20
    elif 50 <= temperature <= 70:
        score += 15
    elif 45 <= temperature <= 75:
        score += 10
    else:
        score += 5
    
    # Aeration (optimal: 3-5 times per week)
    aeration = int(data.get('aeration_frequency', 0))
    if 3 <= aeration <= 5:
        score += 15
    elif 2 <= aeration <= 6:
        score += 10
    else:
        score += 5
    
    # Odor Level (optimal: 1-2)
    odor = int(data.get('odor_level', 5))
    if odor <= 2:
        score += 10
    elif odor <= 3:
        score += 7
    else:
        score += 3
    
    # Decomposition Time (bonus points for faster decomposition)
    days = int(data.get('decomposition_days', 100))
    if days <= 30:
        score += 15
    elif days <= 45:
        score += 10
    elif days <= 60:
        score += 5
    
    return min(score, 100)

def generate_insights(df):
    """Generate analytics insights from experiments data"""
    if df.empty:
        return {}
    
    insights = {
        'summary_stats': {
            'total_experiments': len(df),
            'avg_efficiency_score': round(df['efficiency_score'].mean(), 2),
            'avg_decomposition_days': round(df['decomposition_days'].mean(), 1),
            'best_bin': df.loc[df['efficiency_score'].idxmax(), 'bin_id'],
            'worst_bin': df.loc[df['efficiency_score'].idxmin(), 'bin_id']
        },
        'correlations': {
            'moisture_vs_days': round(df['moisture_level'].corr(df['decomposition_days']), 3),
            'temperature_vs_efficiency': round(df['daily_temperature'].corr(df['efficiency_score']), 3),
            'cn_ratio_vs_npk': round(df['cn_ratio'].corr(df[['final_n', 'final_p', 'final_k']].sum(axis=1)), 3)
        },
        'chart_data': {
            'efficiency_by_bin': df.groupby('bin_id')['efficiency_score'].mean().to_dict(),
            'decomposition_vs_temperature': df[['daily_temperature', 'decomposition_days']].to_dict('records'),
            'npk_values': df[['bin_id', 'final_n', 'final_p', 'final_k']].to_dict('records'),
            'parameter_distribution': {
                'cn_ratio': df['cn_ratio'].tolist(),
                'moisture_level': df['moisture_level'].tolist(),
                'aeration_frequency': df['aeration_frequency'].tolist(),
                'daily_temperature': df['daily_temperature'].tolist()
            }
        },
        'recommendations': generate_recommendations(df)
    }
    
    return insights

def generate_recommendations(df):
    """Generate recommendations based on data analysis"""
    recommendations = []
    
    # Analyze efficiency patterns
    high_efficiency = df[df['efficiency_score'] >= 80]
    if not high_efficiency.empty:
        avg_moisture = high_efficiency['moisture_level'].mean()
        avg_temp = high_efficiency['daily_temperature'].mean()
        avg_cn = high_efficiency['cn_ratio'].mean()
        
        recommendations.append(f"High-efficiency bins maintain moisture around {avg_moisture:.1f}%")
        recommendations.append(f"Optimal temperature range appears to be {avg_temp:.1f}°C")
        recommendations.append(f"Best C/N ratio is around {avg_cn:.1f}")
    
    # Analyze problem areas
    low_efficiency = df[df['efficiency_score'] < 50]
    if not low_efficiency.empty:
        if low_efficiency['odor_level'].mean() > 3:
            recommendations.append("High odor levels indicate need for better aeration")
        if low_efficiency['decomposition_days'].mean() > 60:
            recommendations.append("Slow decomposition may indicate imbalanced C/N ratio")
    
    return recommendations
