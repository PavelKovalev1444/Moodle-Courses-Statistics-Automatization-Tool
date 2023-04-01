from os import listdir, makedirs
from os.path import join, splitext, isdir, basename
import numpy as np
import pandas as pd
import argparse

parser = argparse.ArgumentParser(
    epilog="В зависимости от входных данных, результат либо в директории '<courses>_out', либо в файле <courses>_out.xlsx",
    )
    
parser.add_argument("-c", action ="store", dest='courses', required=True,
                    help="""Информация о курсах. Варианты агрумента: 
                    1. xlsx файлы с результатами прохождения курсов по гиту, линуксу и информатике. 
                    Названия соответствующих файлов ОБЯЗАТЕЛЬНО должны содержать слова `Linux`, `Git`, `0n раздел`
                    """)

parser.add_argument("-s", action ="store", dest='students', required=True,
                    help="""Информация о студентах. Варианты агрумента: 
                    1. Директория с csv файлами (должны называться moevm_data и deans_data)""")

args = parser.parse_args()


def check_extension(file: str, allowed_ext: str or list = 'csv') -> bool:
    file_ext = splitext(file)[1]
    return file_ext == f'.{allowed_ext}' if type(allowed_ext) is str \
        else file_ext in map(lambda x: f'.{x}', allowed_ext)


def get_files(path: str):
    if isdir(path):
        filenames = listdir(path)
        filepaths = list(map(lambda file: join(path, file), filenames))
        files = [file for file in filepaths if check_extension(file, 'csv') or check_extension(file, 'xlsx')]
        return len(files)>0, files
    else:
        return (True, path) if check_extension(path, 'xlsx') else (False, None)


def read_csv(filepath: str) -> pd.DataFrame:
    return pd.read_csv(filepath)


def read_xlsx(filepath: str) -> dict:
    xl = pd.ExcelFile(filepath, engine='openpyxl')
    data = {}
    for sheet in xl.sheet_names:
        data[sheet] = pd.read_excel(filepath, sheet_name=sheet, engine='openpyxl')
    return data


def add_file_by_name_to_dfs_dict(filepath: str, dfs: dict):
    file_basename = basename(filepath)
    name, ext = splitext(file_basename)
    if ext == '.csv':
        data = {name: read_csv(filepath)}
    else:
        data = read_xlsx(filepath)
    dfs.setdefault(name, data)


def read_data(path: str):
    success, files = get_files(path)
    if success:
        dfs = {}
        if type(files) is list:
            for file in files:
                add_file_by_name_to_dfs_dict(file, dfs)
        else:
            add_file_by_name_to_dfs_dict(files, dfs)
        return dfs
    else:
        return None


def refactor_course_info(course: pd.DataFrame):
    return course.rename(
        columns={'Surname': 'last', 'First name': 'first', 
        'Username': 'username', 'Email address': 'email'}, inplace=False)


def save_results(out_dict: dict, in_path_courses:str):
    if isdir(in_path_courses):
        out_dir_name = in_path_courses+'_out'
        makedirs(out_dir_name)
        for title, course_stat in out_dict.items():
            course_stat.to_csv(join(out_dir_name, f'{title}.csv'), index=False)
    else:
        file, ext = splitext(in_path_courses)
        writer = pd.ExcelWriter(f'{file}_out{ext}', engine='openpyxl')
        for title, course_stat in out_dict.items():
            course_stat.to_excel(writer, sheet_name=title)
        writer.save()


# Вспомогательные функции


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


#Для GIT


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


#Для Linux


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
    #count_number_of_tasks_by_column(df, 'External tool') +
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


#Для Pr


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


#Для Cs


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


#Students


def process_students(students: dict):
    #moevm_preprocessing
    students['moevm_data'] = students['moevm_data'].rename(columns={'Адрес электронной почты': 'email', 'Фамилия Имя Отчество': 'ФИО', 
        'Название аккаунта на платформе https://github.com/ (если нет, надо зарегистрироваться)': 'github', 'Номер группы': 'Группа',
        'Ваш никнейм на платформе http://e.moevm.info/ (если нет, надо зарегистрироваться)': 'e.moevm.info',
        'StepikID (если нет, надо зарегистрироваться на https://stepik.org/)': 'Stepik'
    })
    students['moevm_data'] = students['moevm_data'].drop(['Отметка времени', 'Специальность', 'Контактный телефон'#,
    #    'Напишите любые пожелания или вопросы руководству кафедры, относительно предстоящего обучения', 'Расскажите, почему вы поступили учиться на кафедру МОЭВМ?',
    #    'Расскажите, кем хотите работать после окончания обучения?', 'Планируете ли вы обучаться в магистратуре после окончания бакалавриата?',
    #    'Хотели бы вы участвовать в проектах по разработке ПО в процессе обучения?',
    #    'Хотели бы вы участвовать в научных исследованиях, проводимых на кафедре?'
    ], axis=1)
    students['moevm_data'].drop_duplicates(subset=['ФИО'], keep='last', inplace=True)
    students['moevm_data']['email'].str.strip()
    make_col_lower(students['moevm_data'], 'email')

    #deans preprocessing
    students['deans_data'].drop(['Студ. билет', 'Номер дела', 'Факультет', 'Направление', 'Форма', 'Ист. фин.', 'Начало', 'Конец'], axis=1, inplace=True)
    students['deans_data'].rename(columns={'Email': 'email'}, inplace=True)
    students['deans_data']['email'].str.strip()
    make_col_lower(students['deans_data'], 'email')

    #merging
    students['deans_with_github_data'] = students['deans_data'].merge(students['moevm_data'], how='left', left_on='email', right_on='email').rename(
        columns={'Группа_x': 'Группа', 'ФИО_x': 'ФИО'}
    ).drop(['ФИО_y', 'Группа_y'], axis=1)

    #finding without github
    students['without_github'] = students['deans_with_github_data'][students['deans_with_github_data']['github'] != students['deans_with_github_data']['github']]
    
    #writing to csv
    students['deans_with_github_data'].to_csv('./results/students_with_github.csv')
    students['without_github'].to_csv('./results/students_without_github.csv')


def parse_students(students_frame: pd.DataFrame):
    raw_groups_arr = students_frame['Группа'].to_numpy()
    unique_groups = []
    for i in raw_groups_arr:
        if i == i:
            unique_groups.append(i)
    unique_groups = sorted(list(set(unique_groups)))
    groups = {}
    students_frame['github'] = students_frame['github'].str.strip()
    for i in unique_groups:
        groups[i] = students_frame[students_frame['Группа'] == i]
    return groups


def rename_courses(courses: dict):
    renamed_courses = {}
    for i in courses:
        if i.lower().find('git') != -1:
            courses[i].rename(columns={'github аккаунт': 'github'}, inplace=True)
            courses[i]['email'] = courses[i]['email'].str.strip()
            courses[i]['github'] = courses[i]['github'].str.strip()
            renamed_courses['git'] = courses[i]
        elif i.lower().find('01 раздел') != -1:
            courses[i].rename(columns={'github аккаунт': 'github'}, inplace=True)
            courses[i]['email'] = courses[i]['email'].str.strip()
            courses[i]['github'] = courses[i]['github'].str.strip()
            renamed_courses['cs_part_1'] = courses[i]
        elif i.lower().find('02 раздел') != -1:
            courses[i].rename(columns={'github аккаунт': 'github'}, inplace=True)
            courses[i]['email'] = courses[i]['email'].str.strip()
            courses[i]['github'] = courses[i]['github'].str.strip()
            renamed_courses['cs_part_2'] = courses[i]    
        elif i.lower().find('03 раздел') != -1:
            courses[i].rename(columns={'github аккаунт': 'github'}, inplace=True)
            courses[i]['email'] = courses[i]['email'].str.strip()
            courses[i]['github'] = courses[i]['github'].str.strip()
            renamed_courses['cs_part_3'] = courses[i]
        elif i.lower().find('linux') != -1:
            courses[i].rename(columns={'github аккаунт': 'github'}, inplace=True)
            courses[i]['email'] = courses[i]['email'].str.strip()
            courses[i]['github'] = courses[i]['github'].str.strip()
            renamed_courses['linux'] = courses[i]
        elif i.lower().find('контрольная') != -1:
            courses[i].drop(columns=['Country', 'State', 'Started on', 'Completed', 'Time taken'], inplace=True)
            courses[i].rename(columns={'Email address': 'email'}, inplace=True)
            courses[i]['email'] = courses[i]['email'].str.strip()
            courses[i]['email'] = courses[i]['email'].str.lower()
            renamed_courses['kw'] = courses[i][courses[i].columns[:10]]
        else:
            courses[i].drop(columns={'Country', 'State', 'Started on', 'Completed', 'Time taken'}, inplace=True)
            courses[i].rename(columns={'Email address': 'email'}, inplace=True)
            courses[i]['email'] = courses[i]['email'].str.strip()
            courses[i]['email'] = courses[i]['email'].str.lower()
            renamed_courses['cs_add'] = courses[i]
    return renamed_courses        


def merge_email_github(dict_email: dict, dict_github: dict):
    for key in dict_email.keys():
        dict_email_numpy = dict_email[key].to_numpy()
        dict_github_numpy = dict_github[key].to_numpy()
        cols = dict_email[key].columns
        for i in range(dict_email_numpy.shape[0]):
            if dict_email_numpy[i][7] != dict_email_numpy[i][7]:
                if dict_github_numpy[i][7] == dict_github_numpy[i][7]:
                    dict_email_numpy[i] = dict_github_numpy[i]
        dict_email[key] = pd.DataFrame(data=dict_email_numpy, columns=cols)
    return dict_email


def prerequisites_students(dict_dataframes: dict):
    for i in dict_dataframes:
        dict_dataframes[i]['email'].str.strip
        dict_dataframes[i]['github'].str.strip


if __name__ == '__main__':

# Students    
    tmp_students = read_data(args.students)
    students = {}
    for i in tmp_students:
        students.setdefault(i, tmp_students[i][i])
    process_students(students)
    groups = parse_students(students['moevm_data'])

# Courses
    tmp_courses = read_data(args.courses)
    courses = {}
    for i in tmp_courses:
        courses.setdefault(i, tmp_courses[i][list(tmp_courses[i].keys())[0]])
    courses_refactored = {title: refactor_course_info(df) for title, df in courses.items()}
    courses_refactored = rename_courses(courses_refactored)
    courses_refactored['git'] = refactor_git(courses_refactored['git'])
    courses_refactored['linux'] = refactor_linux(courses_refactored['linux'])
    courses_refactored['cs_part_1'] = refactor_cs(courses_refactored['cs_part_1'], 'External tool', 'Внешний инструмент', False)
    courses_refactored['cs_part_2'] = refactor_cs(courses_refactored['cs_part_2'], 'External tool', 'Внешний инструмент', False)
    courses_refactored['cs_part_3'] = refactor_cs(courses_refactored['cs_part_3'], 'External tool', 'Внешний инструмент', False)
    courses_refactored['cs_result'] = make_cs_results(courses_refactored)
    if 'cs_add' in courses_refactored.keys():
        courses_refactored['cs_result'] = add_cs_additional_course(courses_refactored['cs_result'], courses_refactored['cs_add'])
    '''
    courses_refactored['pr'] = refactor_pr(courses_refactored['pr']).copy()
    courses_refactored['cs_additional'] = refactor_cs_additional(courses_refactored['cs_additional']).copy()
    courses_refactored['cs'] = refactor_cs(courses_refactored['cs'], courses_refactored['cs_additional']).copy()
    ''' 


# Merging
    for i in groups:
        tmp_dict_email = {}
        tmp_dict_github = {}

        tmp_dict_email['Git'] = groups[i].merge(courses_refactored['git'], how='left', left_on='email', right_on='email')
        tmp_dict_email['Git'].drop(columns={'github_y', 'first', 'last'}, inplace=True)
        tmp_dict_email['Git'].rename(columns={'github_x': 'github'}, inplace=True)
        
        tmp_dict_email['Linux'] = groups[i].merge(courses_refactored['linux'], how='left', left_on='email', right_on='email')
        tmp_dict_email['Linux'].drop(columns={'github_y', 'first', 'last'}, inplace=True)
        tmp_dict_email['Linux'].rename(columns={'github_x': 'github'}, inplace=True)

        tmp_dict_email['CS part 1'] = groups[i].merge(courses_refactored['cs_part_1'], how='left', left_on='email', right_on='email')
        tmp_dict_email['CS part 1'].drop(columns={'github_y', 'first', 'last'}, inplace=True)
        tmp_dict_email['CS part 1'].rename(columns={'github_x': 'github'}, inplace=True)

        tmp_dict_email['CS part 2'] = groups[i].merge(courses_refactored['cs_part_2'], how='left', left_on='email', right_on='email')
        tmp_dict_email['CS part 2'].drop(columns={'github_y', 'first', 'last'}, inplace=True)
        tmp_dict_email['CS part 2'].rename(columns={'github_x': 'github'}, inplace=True)

        tmp_dict_email['CS part 3'] = groups[i].merge(courses_refactored['cs_part_3'], how='left', left_on='email', right_on='email')
        tmp_dict_email['CS part 3'].drop(columns={'github_y', 'first', 'last'}, inplace=True)
        tmp_dict_email['CS part 3'].rename(columns={'github_x': 'github'}, inplace=True)

        tmp_dict_email['CS results'] = groups[i].merge(courses_refactored['cs_result'], how='left', left_on='email', right_on='email')
        tmp_dict_email['CS results'].drop(columns={'github_y', 'first', 'last'}, inplace=True)
        tmp_dict_email['CS results'].rename(columns={'github_x': 'github'}, inplace=True)

        tmp_dict_email['Контрольная'] = groups[i].merge(courses_refactored['kw'], how='left', left_on='email', right_on='email')
        tmp_dict_email['Контрольная'].drop(columns=['github', 'e.moevm.info', 'Stepik', 'last', 'first', 'username'], inplace=True)


        if 'cs_add' in courses_refactored.keys():
            tmp_dict_email['CS additional'] = groups[i].merge(courses_refactored['cs_add'], how='left', left_on='email', right_on='email')
            tmp_dict_email['CS additional'].drop(columns=['e.moevm.info', 'Stepik', 'last', 'first', 'username'], inplace=True)

        tmp_dict_github['Git'] = groups[i].merge(courses_refactored['git'], how='left', left_on='github', right_on='github')
        tmp_dict_github['Git'].drop(columns={'email_y', 'first', 'last'}, inplace=True)
        tmp_dict_github['Git'].rename(columns={'email_x': 'email'}, inplace=True)

        tmp_dict_github['Linux'] = groups[i].merge(courses_refactored['linux'], how='left', left_on='github', right_on='github')
        tmp_dict_github['Linux'].drop(columns={'email_y', 'first', 'last'}, inplace=True)
        tmp_dict_github['Linux'].rename(columns={'email_x': 'email'}, inplace=True)

        tmp_dict_github['CS part 1'] = groups[i].merge(courses_refactored['cs_part_1'], how='left', left_on='github', right_on='github')
        tmp_dict_github['CS part 1'].drop(columns={'email_y', 'first', 'last'}, inplace=True)
        tmp_dict_github['CS part 1'].rename(columns={'email_x': 'email'}, inplace=True)

        tmp_dict_github['CS part 2'] = groups[i].merge(courses_refactored['cs_part_2'], how='left', left_on='github', right_on='github')
        tmp_dict_github['CS part 2'].drop(columns={'email_y', 'first', 'last'}, inplace=True)
        tmp_dict_github['CS part 2'].rename(columns={'email_x': 'email'}, inplace=True)

        tmp_dict_github['CS part 3'] = groups[i].merge(courses_refactored['cs_part_3'], how='left', left_on='github', right_on='github')
        tmp_dict_github['CS part 3'].drop(columns={'email_y', 'first', 'last'}, inplace=True)
        tmp_dict_github['CS part 3'].rename(columns={'email_x': 'email'}, inplace=True)

        tmp_dict_github['CS results'] = groups[i].merge(courses_refactored['cs_result'], how='left', left_on='github', right_on='github')
        tmp_dict_github['CS results'].drop(columns={'email_y', 'first', 'last'}, inplace=True)
        tmp_dict_github['CS results'].rename(columns={'email_x': 'email'}, inplace=True)

        tmp_dict_github['Контрольная'] = groups[i].merge(courses_refactored['kw'], how='left', left_on='email', right_on='email')
        tmp_dict_github['Контрольная'].drop(columns=['github', 'e.moevm.info', 'Stepik', 'last', 'first', 'username'], inplace=True)

        if 'cs_add' in courses_refactored.keys():
            tmp_dict_github['CS additional'] = groups[i].merge(courses_refactored['cs_add'], how='left', left_on='email', right_on='email')
            tmp_dict_github['CS additional'].drop(columns=['e.moevm.info', 'Stepik', 'last', 'first', 'username'], inplace=True)

        result_dict = merge_email_github(tmp_dict_email, tmp_dict_github)
        
        current_keys = result_dict.keys()
        for j in current_keys:
            result_dict[j].sort_values(by=['ФИО'], inplace=True)
            #result_dict[j].style.hide_index()
            if str(j).find('part') != -1:
                result_dict[j].rename(columns={'total': 'Итого баллов'}, inplace=True)
            elif str(j).find('CS results') != -1:
                result_dict[j].rename(columns={'total_1': 'Раздел 1', 'total_2': 'Раздел 2', 'total_3': 'Раздел 3', 'result': 'Итоговая оценка'}, inplace=True)
            else:
                result_dict[j].rename(columns={'total': 'Итого баллов', 'result': 'Итоговая оценка'}, inplace=True)
        save_results(result_dict, './results/' + str(i)[:4] + '.xlsx')