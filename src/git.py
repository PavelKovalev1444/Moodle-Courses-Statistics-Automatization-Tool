import numpy as np
import pandas as pd


def refactor_git(df: pd.DataFrame):
    make_col_lower(df, 'email')
    for i in df.columns:
        if i.find('Deletion in progress') != -1:
            df.drop(columns=[i], inplace=True)  
        if i.find('Last downloaded from this course') != -1:
            df.drop(columns=[i], inplace=True)    
    new_data_frame = pd.DataFrame(data=df[df.columns[:5]].values, columns=df.columns[:5])
    a = 5
    start = 5
    end = count_number_of_tasks_by_column(df, 'External tool') + start
    for col_name, data in df[df.columns[start:end]].items():
        tmp_data = data.copy()
        for i in range(len(tmp_data)):
            if type(tmp_data[i]) == type(1):
                if tmp_data[i] > 1:
                    tmp_data[i] = 1
        new_data_frame.insert(a, col_name, tmp_data)
        a += 1
    a = end    
    for col_name, data in df[df.columns[end:]].items():
        new_data_frame.insert(a, col_name, data)
        a+=1
    new_data_frame = total_tasks_and_points_count_git(new_data_frame)
    return new_data_frame   
            

def total_tasks_and_points_count_git(df: pd.DataFrame):
    tmp_df = pd.DataFrame(data=df[df.columns[:5]].values, columns=df.columns[:5])
    df_numpy = df[df.columns[6:]].to_numpy()
    points_counter = 0
    marks_array = []
    points_counter_array = []
    for i in range(df_numpy.shape[0]):
        for j in range(df_numpy.shape[1]):
            if type(df_numpy[i][j]) == type(1):
                if df_numpy[i][j] > 0:
                    points_counter += df_numpy[i][j]
        points_counter_array.append(points_counter)
        points_counter = 0
    max_points = count_number_of_tasks_by_column(df[df.columns[6:]], 'External tool') + count_points_for_tasks(df[df.columns[6:]], 'Quiz')
    for i in range(len(points_counter_array)):
        marks_array.append(np.floor((points_counter_array[i]/max_points) * 3))  
    tmp_df.insert(5, 'total', points_counter_array) # сумма баллов с гита
    tmp_df.insert(6, 'result', marks_array) # оценка за курс
    index = 7
    for col_name, data in df[df.columns[6:]].items():
        tmp_df.insert(index, col_name, data)
        index += 1
    return tmp_df