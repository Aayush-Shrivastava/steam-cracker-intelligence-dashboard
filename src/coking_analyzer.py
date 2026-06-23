import numpy as np
import pandas as pd

"""Coking rate calculation and statistical analysis"""

def calculate_coking_rates(cycle_df: pd.DataFrame,time_col: str = 'run_length_hours',pressure_col: str = 'pressure_drop_bar')->list[tuple[float,float]]:

    """ Calculate coking rate for a single cycle using linear regression
    Args:
        cycle_df (pd.DataFrame): Data for one cycle
    Returns:
        tuple: (slope_bar_per_hour, intercept_bar)"""
  
    x = cycle_df[time_col].values 
    y = cycle_df[pressure_col].values
    c=np.polyfit(x,y,1)
    slope_per_hr = c[0]
    intercept = c[1]
    
    return slope_per_hr,intercept

def analyze_all_cycles(df: pd.DataFrame,cycles: list[tuple[int,int]],time_col: str = 'run_length_hours',pressure_col: str = 'pressure_drop_bar')->list[int,float,float]:
    
    """Calculate coking rate for all cycles
    Args:
        df (pd.DataFrame): Full dataset
        cycles (list): List of (start, end) index tuples
        time_col (str): Time column name
        pressure_col (str): Pressure column name
    Returns:
        list: [(cycle_num, rate_bar_per_day, intercept), ...]"""
    
    result = []
    for cycle_num, (start_idx, end_idx) in enumerate(cycles, start=1):
        cycle_df = df.loc[start_idx:end_idx].copy()
        slope_per_hour, intercept = calculate_coking_rates(cycle_df, time_col, pressure_col)
        rate_per_day = slope_per_hour * 24
        result.append((cycle_num, rate_per_day, intercept))
    
    return result

def calculate_statistics(result: list[int,float,float])->dict[str,float]:

    """Calculate summary statistics for coking rates
    Args:
        results (list): [(cycle_num, rate, intercept), ...]
    Returns:
        dict: Statistics summary"""
    
    rates = [rate for _, rate, _ in result]
    if not rates:
        return {"Mean Rate": 0.0, "Standard Deviation": 0.0, "Minimum Rate": 0.0, 
                "Maximum Rate": 0.0, "Cycles": 0, "Variance": 0.0, "Coefficient of Variation(%)": 0.0}
    
    mean_rate=np.mean(rates)
    std_rate=np.std(rates,ddof=1)
    min_rate=np.min(rates)
    max_rate=np.max(rates)
    cv=(std_rate/mean_rate)*100
    cycles=len(result)
    variance=np.var(rates,ddof=1)
    stats={"Mean Rate": mean_rate,
         "Standard Rate": std_rate,
         "Minimum Rate": min_rate,
         "Maximum Rate": max_rate,
         "Cycles": cycles,
         "Variance": variance,
         "Coefficient of variance(%)": cv}
    
    return stats



def print_summary(results: list[tuple[int, float, float]], stats: dict[str, float]) -> None:

    """Print formatted analysis summary
    Args:
        results: List of (cycle_num, rate, intercept) tuples
        stats: Statistics dictionary from calculate_statistics() """
    
    # Header
    print("\n" + "=" * 50)
    print("COKING RATE ANALYSIS - SUMMARY:\n")
    print("=" * 50)
    
    # Statistics printing section
    print(f"\nCycles analyzed: {stats['Cycles']}")
    print(f"Average rate: {stats['Mean Rate']:.4f} bar/day")
    print(f"Std deviation: {stats['Standard Rate']:.4f} bar/day")
    print(f"Variance: {stats['Variance']:.4f} bar/day")
    print(f"Range: {stats['Minimum Rate']:.4f} to {stats['Maximum Rate']:.4f} bar/day")
    print(f"Coefficient of variation: {stats['Coefficient of variance(%)']:.2f}%")
    
    # Table header
    print(f"\n{'Cycle':>6} | {'Rate (bar/day)':>15} | {'Deviation':>12}")
    print("-" * 40)
    
    # Table rows - loop through each result
    for cycle_num, rate, _ in results:
        # Calculate deviation from mean
        deviation = rate - stats['Mean Rate']
        
        # Print row
        print(f"{cycle_num:6d} | {rate:15.4f} | {deviation:+12.4f}")
    
    # Footer
    print("=" * 50 + "\n")
    
    # Interpretation
    print("=== INTERPRETATION ===")
    
    # Interpret consistency based on CV
    cv = stats['Coefficient of variance(%)']
    if cv < 3:
        consistency = "Highly consistent operation"
        interpretation = "Indicates stable feed quality and good process control"
    elif cv < 7:
        consistency = "Normal operational variation"
        interpretation = "Typical for industrial operations"
    else:
        consistency = "High variability detected"
        interpretation = "Investigate: feed quality changes, operating condition drift, or control issues"
    
    print(f"Consistency: {consistency}")
    print(f"Analysis: {interpretation}")
    
    # Predicted run length
    avg_rate_per_hour = stats['Mean Rate'] / 24
    start_dp = 0.8  # bar (from data generation)
    threshold = 3.0  # bar (approximate from generation: 0.8 + 720*0.003)
    
    hours_to_threshold = (threshold - start_dp) / avg_rate_per_hour
    days_to_threshold = hours_to_threshold / 24
    
    print(f"\nPredicted run length: {days_to_threshold:.1f} days")
    print(f"Actual cycle length: 30 days")
    print(f"Prediction accuracy: {(days_to_threshold/30)*100:.1f}%")
    print("=" * 50 + "\n")