import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from coking_analyzer import calculate_coking_rates

"""Plotting functions for coking analysis"""

def plot_single_cycle(df: pd.DataFrame,cycle_num: int,cycles: list[tuple[int, int]],threshold: float = 2.9) -> go.Figure:

    """Plot detailed analysis for a single cycle
    Args:
        df: Full dataset
        cycle_num: Which cycle to plot (1-13)
        cycles: List of cycle boundaries
        threshold: Decoke limit
    Returns:
        Plotly Figure"""
    
    start_idx,end_idx=cycles[cycle_num-1]
    print(f"Cycle {cycle_num}: rows {start_idx} to {end_idx}")
    cycle_data=df.loc[start_idx:end_idx].copy()
    print(f"Extracted {len(cycle_data)} data points")
    print(f"Hours: {cycle_data['run_length_hours'].min()} to {cycle_data['run_length_hours'].max()}")
    slope, intercept = calculate_coking_rates(cycle_data)
    print(f"Coking rate: {slope*24:.4f} bar/day")
    fig=px.line(cycle_data,x='run_length_hours',y='pressure_drop_bar',title=f'Cycle {cycle_num} Detailed Analysis',labels={'run_length_hours': 'Run Time (hours)','pressure_drop_bar': 'Pressure Drop (bar)'})
    fig.update_layout(template='plotly_white')
    x_values=cycle_data['run_length_hours'].values
    y_pred=slope*x_values+intercept
    fig.add_trace(go.Scatter(x=x_values,y=y_pred,mode='lines',name=f'Trend ({slope*24:.4f} bar/day)',line=dict(color='red', width=3)))
    fig.add_hline( y=threshold,line_dash='dot',line_color='orange',annotation_text=f'Decoke Threshold ({threshold} bar)')
    return fig

def plot_rate_comparison(results: list[tuple[int, float, float]],stats: dict[str, float]) -> go.Figure:
    
    """Bar chart comparing coking rates across cycles
    Args:
        results: List of (cycle_num, rate_bar_per_day, intercept)
        stats: Statistics dictionary from calculate_statistics()
    Returns:
        Plotly Figure"""
    
    CNO = []
    rates = []
    for i in range(len(results)):
        cycle = results[i][0]
        rate = results[i][1]
        CNO.append(cycle)
        rates.append(rate)

    colors = []
    for rate in rates:
        if rate >= stats['Mean Rate']:
            colors.append('Orange')
        else:
            colors.append('Green')

    fig = go.Figure()
    fig.add_trace(go.Bar(x=CNO,y=rates,marker_color=colors,text=[f'{r:.4f}' for r in rates],textposition='outside',name='Coking Rate',hovertemplate='<b>Cycle %{x}</b><br>' +'Rate: %{y:.4f} bar/day<extra></extra>'))
    fig.add_trace(go.Scatter(x=[min(CNO), max(CNO)],y=[stats['Mean Rate'], stats['Mean Rate']],mode='lines',name=f'Average: {stats["Mean Rate"]:.4f} bar/day',line=dict(color='Red', width=2, dash='dash'),showlegend=True,hovertemplate=f'Average: {stats["Mean Rate"]:.4f} bar/day<extra></extra>'))
    
    # ===== ZOOM ======
    min_rate = min(rates)
    max_rate = max(rates)
    rate_range = max_rate - min_rate
    
    y_min = min_rate - (rate_range * 0.1)
    y_max = max_rate + (rate_range * 0.15) 
    
    fig.update_layout(title='Coking Rate Comparison Across Cycles',xaxis_title='Cycle Number',yaxis_title='Coking Rate (bar/day)',template='plotly_white',width=1500,height=700,showlegend=True,yaxis=dict(range=[y_min, y_max], dtick=(rate_range / 10) ), annotations=[dict(text="⚠️ Y-axis zoomed to highlight differences (does not start at 0)",xref="paper", yref="paper",x=0.5, y=-0.15,showarrow=False,font=dict(size=11, color="gray"),xanchor='center')])
    return fig

def multiple_plot_comparison(df: pd.DataFrame,cycle_nums: list[int],cycles: list[tuple[int, int]],threshold: float = 2.9) -> go.Figure:

    """Plot comparitive analysis for multiple cycles
    Args:
        df: Full dataset
        cycle_nums: Which cycles to plot (1-13)
        cycles: List of cycle boundaries
        threshold: Decoke limit
    Returns:
        Plotly Figure"""
    
    fig = go.Figure()
    colors = ['blue', 'green', 'orange', 'purple']
    print(f"\n=== Plotting cycles: {cycle_nums} ===")
    for i, cycle_num in enumerate(cycle_nums):
        color=colors[i]
        print(f"\nProcessing Cycle {cycle_num}...")
        cycle_index = cycle_num - 1
        start_idx, end_idx = cycles[cycle_index]
        cycle_data = df.loc[start_idx:end_idx].copy()
        print(f"  Data points: {len(cycle_data)}")
        slope, intercept = calculate_coking_rates(cycle_data)
        print(f"  Slope: {slope*24:.4f} bar/day")
        print(f"  Intercept: {intercept:.3f} bar")
        x_vals = cycle_data['run_length_hours'].values
        y_pred = slope * x_vals + intercept
        print(f"  Predicted ΔP range: {y_pred.min():.2f} to {y_pred.max():.2f} bar")
        fig.add_trace(go.Scatter(x=cycle_data['run_length_hours'],y=cycle_data['pressure_drop_bar'],mode='markers',line=dict(color=color, width=0.5),opacity=0.2,showlegend=True,hoverinfo='skip',name=f'Cycle {cycle_num} data'))
        fig.add_trace(go.Scatter(x=x_vals,y=y_pred,mode='lines',name=f'Cycle {cycle_num} ({slope*24:.4f} bar/day)',line=dict(color=colors[i], width=1)))
        print(f"  ✓ Added trace")

    fig.add_hline(y=threshold,line_dash='dot',line_color='red',line_width=2,annotation_text=f'Decoke Threshold ({threshold} bar)',annotation_position='top left')
    fig.update_layout(title=f'Cycles Comparison: {", ".join(map(str, cycle_nums))}',xaxis_title='Run Time (hours)',yaxis_title='Pressure Drop (bar)',template='plotly_white',width=1500,height=700,hovermode='closest')
    
    return fig

        


