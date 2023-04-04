from os import listdir, makedirs
from os.path import join, splitext, isdir, basename
import numpy as np
import pandas as pd
import argparse

import students as st
import cs as cs
import git as git
import linux as linux


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


def rename_courses(courses: dict):
    renamed_courses = {}
    for i in courses:
        if i.lower().find('git') != -1:
            courses[i].rename(columns={'github аккаунт': 'github'}, inplace=True)
            courses[i]['email'] = courses[i]['email'].str.strip()
            courses[i]['github'] = courses[i]['github'].str.strip()
            renamed_courses['git'] = courses[i]
        elif i.lower().find('раздел') != -1:
            index = i.lower().find('раздел')
            new_name = 'cs_part_' + str(int(i.lower()[index-3:index]))
            courses[i].rename(columns={'github аккаунт': 'github'}, inplace=True)
            courses[i]['email'] = courses[i]['email'].str.strip()
            courses[i]['github'] = courses[i]['github'].str.strip()
            renamed_courses[new_name] = courses[i]
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


def get_student_groups():
    tmp_students = read_data(args.students)
    students = {}
    for i in tmp_students:
        students.setdefault(i, tmp_students[i][i])
    st.process_students(students)
    return st.parse_students(students['moevm_data'])


def get_courses():
    tmp_courses = read_data(args.courses)
    courses = {}
    for i in tmp_courses:
        courses.setdefault(i, tmp_courses[i][list(tmp_courses[i].keys())[0]])
    tmp_courses = {title: refactor_course_info(df) for title, df in courses.items()}
    return rename_courses(tmp_courses)


def refactoring(courses: dict):
    courses_refactored = {}
    for i in courses:
        if i.lower().find('cs_part') != -1:
            courses_refactored[i] = cs.refactor_cs(courses[i], 'External tool', 'Внешний инструмент', False)
        #    print('Refactored ' + i + ' course')
        elif i.lower().find('linux') != -1:
            courses_refactored['linux'] = linux.refactor_linux(courses['linux'])
        #    print('Refactored ' + i + ' course')
        elif i.lower().find('kw') != -1:
                courses_refactored['kw'] = courses['kw']
        #    print('Refactored ' + i + ' course')
        elif i.lower().find('git') != -1:
            courses_refactored['git'] = git.refactor_git(courses['git'])
        #    print('Refactored ' + i + ' course')
        elif i.lower().find('cs_add') != -1:
            courses_refactored['cs_add'] = courses['cs_add']
            print('Refactored ' + i + ' course')
    return courses_refactored


def merge_by_email(group: pd.DataFrame, courses: dict):
    tmp_dict_email = {}
    for i in courses:
        tmp_dict_email[i] = group.merge(courses[i], how='left', left_on='email', right_on='email')
        tmp_columns = tmp_dict_email[i].columns
        if 'github_y' in tmp_columns:
            tmp_dict_email[i].drop(columns={'github_y'}, inplace=True)
        if 'first' in tmp_columns:
            tmp_dict_email[i].drop(columns={'first'}, inplace=True)
        if 'last' in tmp_columns:
            tmp_dict_email[i].drop(columns={'last'}, inplace=True)
        if 'github_x' in tmp_columns:
            tmp_dict_email[i].rename(columns={'github_x': 'github'}, inplace=True)
    return tmp_dict_email


def merge_by_github(group: pd.DataFrame, courses: dict):
    tmp_dict_github = {}
    for i in courses:
        if i == 'kw' or i =='cs_add':
            tmp_dict_github[i] = group.merge(courses[i], how='left', left_on='email', right_on='email')
        else:
            tmp_dict_github[i] = group.merge(courses[i], how='left', left_on='github', right_on='github')
        tmp_columns = tmp_dict_github[i].columns
        if 'email_y' in tmp_columns:
            tmp_dict_github[i].drop(columns={'email_y'}, inplace=True)
        if 'first' in tmp_columns:
            tmp_dict_github[i].drop(columns={'first'}, inplace=True)
        if 'last' in tmp_columns:
            tmp_dict_github[i].drop(columns={'last'}, inplace=True)
        if 'email_x' in tmp_columns:
            tmp_dict_github[i].rename(columns={'email_x': 'email'}, inplace=True)
    return tmp_dict_github


def merge_all(groups: dict, courses: dict):
    for i in groups:
        tmp_dict_email = merge_by_email(groups[i], courses)
        tmp_dict_github = merge_by_github(groups[i], courses)
        result_dict = merge_email_github(tmp_dict_email, tmp_dict_github)
        current_keys = result_dict.keys()
        for j in current_keys:
            result_dict[j].sort_values(by=['ФИО'], inplace=True)
            if str(j).find('part') != -1:
                result_dict[j].rename(columns={'total': 'Итого баллов'}, inplace=True)
            elif str(j).find('result') != -1:
                result_dict[j].rename(columns={'total_1': 'Раздел 1', 'total_2': 'Раздел 2', 'total_3': 'Раздел 3', 'result': 'Итоговая оценка'}, inplace=True)
            else:
                result_dict[j].rename(columns={'total': 'Итого баллов', 'result': 'Итоговая оценка'}, inplace=True)
        save_results(result_dict, './../results/' + str(i)[:4] + '.xlsx')


if __name__ == '__main__':

    # getting students from input data
    groups = get_student_groups()

    # getting courses from input data
    courses = get_courses()

    courses_refactored = refactoring(courses)
    courses_refactored['cs_result'] = cs.make_cs_results(courses_refactored)
    if 'cs_add' in courses_refactored.keys():
        courses_refactored['cs_result'] = cs.add_cs_additional_course(courses_refactored['cs_result'], courses_refactored['cs_add'])
    merge_all(groups, courses_refactored)

# Merging
    '''
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
            result_dict[j].style.hide_index()
            if str(j).find('part') != -1:
                result_dict[j].rename(columns={'total': 'Итого баллов'}, inplace=True)
            elif str(j).find('CS results') != -1:
                result_dict[j].rename(columns={'total_1': 'Раздел 1', 'total_2': 'Раздел 2', 'total_3': 'Раздел 3', 'result': 'Итоговая оценка'}, inplace=True)
            else:
                result_dict[j].rename(columns={'total': 'Итого баллов', 'result': 'Итоговая оценка'}, inplace=True)
        save_results(result_dict, './results/' + str(i)[:4] + '.xlsx')
    '''