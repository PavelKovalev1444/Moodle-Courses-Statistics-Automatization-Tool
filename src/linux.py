import numpy as np
import pandas as pd


def refactor_linux(df: pd.DataFrame):
    make_col_lower(df, 'email')
    df.drop(columns=['External tool: Команда man (Real)', 'External tool: Горячие клавиши (Real)'], inplace=True)
    for i in df.columns:
        if i.find('Lesson') != -1:
            df.drop(columns=[i], inplace=True)  
        if i.find('Last downloaded from this course') != -1:
            df.drop(columns=[i], inplace=True)
    tmp_df = pd.DataFrame()
    idx = 0
    for col_name, data in df[df.columns].items():
        if col_name.find('External tool') != -1:
            tmp_data = data.copy()
            for i in range(len(tmp_data)):
                if type(tmp_data[i]) == type(1):
                    if tmp_data[i] > 1:
                        tmp_data[i] = 1
            tmp_df.insert(idx, col_name, tmp_data)                
            idx += 1
        elif col_name.find('Итого') == -1:
            tmp_df.insert(idx, col_name, data)
            idx += 1
    tmp_df = total_tasks_and_points_count_linux(tmp_df)
    return tmp_df


def total_tasks_and_points_count_linux(df: pd.DataFrame):
    tmp_df = pd.DataFrame(data=df[df.columns[:5]].values, columns=df.columns[:5])
    df_numpy = df[df.columns[5:]].to_numpy()
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
    max_points = count_points_for_tasks(df, 'External tool') + count_points_for_tasks(df, 'Quiz')
    for i in range(len(points_counter_array)):
        marks_array.append(np.floor((points_counter_array[i]/max_points) * 3))  
    tmp_df.insert(5, 'total', points_counter_array) # сумма баллов с линукса
    tmp_df.insert(6, 'result', marks_array) # оценка за курс
    idx = 7
    for col_name, data in df[df.columns[5:]].items():
        tmp_df.insert(idx, col_name, data)
        idx += 1
    return tmp_df