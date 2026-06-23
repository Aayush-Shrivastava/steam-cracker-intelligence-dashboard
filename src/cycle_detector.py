import pandas as pd

"""Cycle detection utilitie(s) for identifying run boundaries."""

def detect_cycles(df: pd.DataFrame,pressure_col: str = 'pressure_drop_bar', threshold: float = -1)->list[tuple[int,int]]:

    """Detects cycle boundaries by finding pressure drop resets (decoke events)
    Args:
        df (pd.DataFrame): Cracking data
        pressure_col (str): Column name for pressure drop
        threshold (float): ΔP drop threshold indicating decoke (bar)
    Returns:
        list: List of (start_idx, end_idx) tuples for each cycle."""
    
    delp_diff=df[pressure_col].diff()
    decoke_points=df[delp_diff<=threshold].index.tolist()
    cycles=[]
    start=0
    for i in decoke_points:
        cycles.append((start+1,i))
        start=i+1
    cycles.append((start,len(df)-1)) # Last cycle
    return cycles