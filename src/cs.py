import numpy as np
import pandas as pd


def refactor_cs(df: pd.DataFrame, col_name_refactor: str, rus_col_name_refactor: str, is_result: bool):
    make_col_lower(df, 'email')
    tmp_df = pd.DataFrame(data=df[df.columns[:5]].values, columns=df.columns[:5])
    idx = 5
    for col_name, data in df[df.columns].items():
        if col_name.find(rus_col_name_refactor) != -1 or col_name.find(col_name_refactor) != -1 :
            tmp_data = data.copy()
            for i in range(len(tmp_data)):
                if type(tmp_data[i]) == type(1):
                    if tmp_data[i] > 1:
                        tmp_data[i] = 1
            tmp_df.insert(idx, col_name, tmp_data)                
            idx += 1
        elif col_name.find('Quiz') != -1:
            tmp_df.insert(idx, col_name, data)
            idx += 1        
    total_tasks_and_points_count_cs(tmp_df, is_result)
    return tmp_df


def total_tasks_and_points_count_cs(df: pd.DataFrame, is_result: bool):
    df_numpy = df[df.columns[5:]].to_numpy()
    points_counter = 0
    points_counter_array = []
    if is_result:
        for i in range(df_numpy.shape[0]):
            for j in range(df_numpy.shape[1]):
                if df_numpy[i][j] == df_numpy[i][j]:
                    points_counter += int(df_numpy[i][j])
            points_counter_array.append(points_counter)
            points_counter = 0        
        marks_array = []
        max_points = int(count_points_for_tasks(df, 'total'))
        for i in range(len(points_counter_array)):
            cur_mark = np.floor((points_counter_array[i]/max_points) * 5)
            if cur_mark - 5.0 > 0.0:
                marks_array.append(5)  
            else:
                marks_array.append(cur_mark)     
        df.insert(5, 'result', marks_array)
    else:
        for i in range(df_numpy.shape[0]):
            for j in range(df_numpy.shape[1]):
                if type(df_numpy[i][j]) == type(1) or type(df_numpy[i][j]) == type(np.int64(1)) :
                    if df_numpy[i][j] > 0:
                        points_counter += int(df_numpy[i][j])
            points_counter_array.append(points_counter)
            points_counter = 0
        df.insert(5, 'total', points_counter_array)


def add_cs_additional_course(df_result: pd.DataFrame, df_additional: pd.DataFrame):
    df_result = df_result.merge(df_additional, how='left', left_on='email', right_on='email')
    df_result.rename(columns={'first_x' : 'first', 'last_x': 'last', 'username_x' : 'username'}, inplace=True)
    df_result.drop(columns=['last_y', 'first_y', 'username_y'], inplace=True)
    for i in df_result.columns:
        if i.find('Q.') != -1:
            df_result.drop(columns=[i], inplace=True)
    df_result_columns = df_result.columns
    df_result_numpy = df_result.to_numpy()
    for i in range(df_result.shape[0]):
        if df_result_numpy[i][9] == '4.00':
            df_result_numpy[i][5] = df_result_numpy[i][5] + 1
            if df_result_numpy[i][5] > 5: 
                df_result_numpy[i][5] = 5
    df_result = pd.DataFrame(data=df_result_numpy, columns=df_result_columns)
    return df_result


def make_cs_results(courses_refactored: dict):
    result_df = courses_refactored['cs_part_1'][courses_refactored['cs_part_1'].columns[:5]].copy()
    
    result_df = result_df.merge(courses_refactored['cs_part_1'], how='left', left_on='github', right_on='github')
    result_df.rename(columns={'last_x': 'last', 'first_x': 'first', 'username_x': 'username', 'email_x': 'email', 'total': 'total_1'}, inplace=True)
    result_df.drop(columns=['first_y', 'last_y', 'username_y', 'email_y'], inplace=True)
    for i in result_df.columns:
        if i.find('Quiz') != -1 or i.find('External tool') != -1:
            result_df.drop(columns=[i], inplace=True)

    result_df = result_df.merge(courses_refactored['cs_part_2'], how='left', left_on='github', right_on='github')
    result_df.rename(columns={'last_x': 'last', 'first_x': 'first', 'username_x': 'username', 'email_x': 'email', 'total': 'total_2'}, inplace=True)
    result_df.drop(columns=['first_y', 'last_y', 'username_y', 'email_y'], inplace=True)
    for i in result_df.columns:
        if i.find('Quiz') != -1 or i.find('External tool') != -1:
            result_df.drop(columns=[i], inplace=True)

    result_df = result_df.merge(courses_refactored['cs_part_3'], how='left', left_on='github', right_on='github')
    result_df.rename(columns={'last_x': 'last', 'first_x': 'first', 'username_x': 'username', 'email_x': 'email', 'total': 'total_3'}, inplace=True)
    result_df.drop(columns=['first_y', 'last_y', 'username_y', 'email_y'], inplace=True)
    for i in result_df.columns:
        if i.find('Quiz') != -1 or i.find('External tool') != -1:
            result_df.drop(columns=[i], inplace=True)
    return refactor_cs(result_df, 'total', 'total', True)