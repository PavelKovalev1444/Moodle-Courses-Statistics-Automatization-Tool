def refactor_pr(df: pd.DataFrame):
    tmp_df = pd.DataFrame()
    idx = 0
    for col_name, data in df[df.columns].items():
        if col_name.find('Внешний инструмент') != -1 or col_name.find('External tool') != -1 :
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
    tmp_df = total_tasks_and_points_count_pr(tmp_df)
    return tmp_df


def total_tasks_and_points_count_pr(df: pd.DataFrame):
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
    max_points = count_number_of_tasks_by_column(df, 'Внешний инструмент') + 10*count_number_of_tasks_by_column(df, 'Тест')
    for i in range(len(points_counter_array)):
        marks_array.append(np.floor((points_counter_array[i]/max_points) * 5))  
    tmp_df.insert(5, 'total', points_counter_array) # сумма баллов с линукса
    tmp_df.insert(6, 'result', marks_array) # оценка за курс
    idx = 7
    for col_name, data in df[df.columns[7:]].items():
        tmp_df.insert(idx, col_name, data)
        idx += 1
    return tmp_df