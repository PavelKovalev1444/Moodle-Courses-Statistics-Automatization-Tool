import numpy as np
import pandas as pd
from helpers import make_col_lower


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
    students['moevm_data']['email'] = students['moevm_data']['email'].str.strip()
    make_col_lower(students['moevm_data'], 'email')

    #deans preprocessing
    students['deans_data'].drop(['Студ. билет', 'Номер дела', 'Факультет', 'Направление', 'Форма', 'Ист. фин.', 'Начало', 'Конец'], axis=1, inplace=True)
    students['deans_data'].rename(columns={'Email': 'email'}, inplace=True)
    students['deans_data']['email'] = students['deans_data']['email'].str.strip()
    make_col_lower(students['deans_data'], 'email')

    #merging
    students['deans_with_github_data'] = students['deans_data'].merge(students['moevm_data'], how='left', left_on='email', right_on='email').rename(
        columns={'Группа_x': 'Группа', 'ФИО_x': 'ФИО'}
    ).drop(['ФИО_y', 'Группа_y'], axis=1)

    #finding without github
    students['without_github'] = students['deans_with_github_data'][students['deans_with_github_data']['github'] != students['deans_with_github_data']['github']]
    
    #writing to csv
    students['deans_with_github_data'].to_csv('./../results/students_with_github.csv')
    students['without_github'].to_csv('./../results/students_without_github.csv')


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