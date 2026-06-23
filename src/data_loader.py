import pandas as pd

"""Data loading and preprocessing utilitie(s)."""

def load(filepath)->pd.DataFrame:

    """Loads the cracking data CSV and prepares it for analysis
    Args:filepath (str): Path to CSV file
    Returns: pd.DataFrame: Loaded data with timestamp parsed."""

    df=pd.read_csv(filepath)
    df['timestamp']=pd.to_datetime(df['timestamp']) #Converting the default datatype from string to timestamp
    df.index.name='Data point'
    return df