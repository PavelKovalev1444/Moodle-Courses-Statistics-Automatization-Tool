import numpy as np
import pandas as pd


def count_number_of_tasks_by_column(df: pd.DataFrame, col_name):
    count = 0
    for i in df.columns:
        if i.find(col_name) != -1:
            count += 1
    return count     


def count_points_for_tasks(df: pd.DataFrame, col_name: str):
    count = 0
    for i in df.columns:
        if i.find(col_name) != -1:
            df_numpy = df[i].to_numpy()
            arr = []
            for e in range(df_numpy.shape[0]):
                if type(df_numpy[e]) == type(1) or type(df_numpy[e]) == type(np.int64(1)) or type(df_numpy[e]) == type(np.float64(1.0)):
                    if df_numpy[e] == df_numpy[e]:
                        arr.append(df_numpy[e])        
            if len(arr) > 0:
                count += max(arr)            
    return count 


def make_col_lower(df: pd.DataFrame, col_name: str):
    new_emails = []
    for i in df[col_name]:
        if (i == i):
            new_emails.append(i.lower())
        else:
            new_emails.append(i)
    df[col_name] = new_emails