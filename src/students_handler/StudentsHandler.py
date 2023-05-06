from data_reader.DataReader import DataReader

class StudentsHandler(object):
    
    def __init__(self, students_info):
        self.data_reader = DataReader()
        self.students_deans = students_info["studentsDeans"]
        self.students_cathedra = students_info["studentsCathedra"]
    
    def get_student_groups(self):
        tmp_students = []
        paths = [
            self.students_deans["path"],
            self.students_cathedra["path"]
        ]
        for i in paths:
            tmp_students.append(self.data_reader.read_data(i))
        self.students = {}
        for students_data in tmp_students:
            for i in students_data:
                if i.find("deans") != -1:
                    self.students.setdefault("studentsDeans", students_data[i][i])
                else: 
                    self.students.setdefault("studentsCathedra", students_data[i][i])
        self.handle_students_deans()
        self.handle_students_cathedra()
        #self.handle_students()
        #return sНазваниеt.parse_students(students['moevm_data'])
        return self.students


    def handle_students_deans(self):
        all_columns = list(self.students["studentsDeans"].columns)
        columns_to_drop = []
        for i in all_columns:
            if i not in self.students_deans["fixedColumns"]:
                columns_to_drop.append(i)
        self.students["studentsDeans"].drop(columns_to_drop, inplace=True, axis=1)
        self.students["studentsDeans"].rename(columns=self.students_deans["renameSettings"], inplace=True)
        self.students["studentsDeans"].drop_duplicates(subset=self.students_deans["duplicatesSubset"], keep='last', inplace=True)


    def handle_students_cathedra(self):
        all_columns = list(self.students["studentsCathedra"].columns)
        columns_to_drop = []
        for i in all_columns:
            if i not in self.students_cathedra["fixedColumns"]:
                columns_to_drop.append(i)
        self.students["studentsCathedra"].drop(columns_to_drop, inplace=True, axis=1)
        self.students["studentsCathedra"].rename(columns=self.students_cathedra["renameSettings"], inplace=True)
        self.students["studentsCathedra"].drop_duplicates(subset=self.students_cathedra["duplicatesSubset"], keep='last', inplace=True)

    
    def merge_all_students(self):
        pass

    

    def handle_students():
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