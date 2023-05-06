from data_reader.DataReader import DataReader

class StudentsHandler(object):
    
    def __init__(self, students_info):
        self.data_reader = DataReader()
        self.students_info = students_info
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
        self.merge_all_students()
        return self.students['merged_students']


    def handle_students_deans(self):
        all_columns = list(self.students["studentsDeans"].columns)
        columns_to_drop = []
        for i in all_columns:
            if i not in self.students_deans["fixedColumns"]:
                columns_to_drop.append(i)
        self.students["studentsDeans"].drop(columns_to_drop, inplace=True, axis=1)
        self.students["studentsDeans"].rename(columns=self.students_deans["renameSettings"], inplace=True)
        self.students["studentsDeans"].drop_duplicates(subset=self.students_deans["duplicatesSubset"], keep='last', inplace=True)
        if "email" in self.students["studentsDeans"].columns:
            self.students["studentsDeans"]["email"] = self.students["studentsDeans"]["email"].str.strip()
            self.students["studentsDeans"]["email"] = self.students["studentsDeans"]["email"].str.lower()


    def handle_students_cathedra(self):
        all_columns = list(self.students["studentsCathedra"].columns)
        columns_to_drop = []
        for i in all_columns:
            if i not in self.students_cathedra["fixedColumns"]:
                columns_to_drop.append(i)
        self.students["studentsCathedra"].drop(columns_to_drop, inplace=True, axis=1)
        self.students["studentsCathedra"].rename(columns=self.students_cathedra["renameSettings"], inplace=True)
        self.students["studentsCathedra"].drop_duplicates(subset=self.students_cathedra["duplicatesSubset"], keep='last', inplace=True)
        if "email" in self.students["studentsCathedra"].columns:
            self.students["studentsCathedra"]["email"] = self.students["studentsCathedra"]["email"].str.strip()
            self.students["studentsCathedra"]["email"] = self.students["studentsCathedra"]["email"].str.lower()
        if "github" in self.students["studentsCathedra"].columns:
            self.students["studentsCathedra"]["github"] = self.students["studentsCathedra"]["github"].str.strip()
            self.students["studentsCathedra"]["github"] = self.students["studentsCathedra"]["github"].str.lower()

    
    def merge_all_students(self):
        self.students['merged_students'] = self.students["studentsDeans"].merge(
            self.students["studentsCathedra"], 
            how='left', 
            left_on='email', 
            right_on='email'
        )
        columns_to_drop = []
        columns_to_rename = {}
        for i in self.students['merged_students'].columns:
            if i.find('_x') != -1:
                columns_to_rename[i] = i[0:-2]
            elif i.find('_y') != -1:
                columns_to_drop.append(i)
        self.students['merged_students'].drop(columns_to_drop, inplace=True, axis=1)
        self.students['merged_students'].rename(columns=columns_to_rename, inplace=True)
    
    def parse_students_into_groups(self):
        groups_list = self.students['merged_students'][self.students_info["groupColumnName"]].unique()
        groups = {}
        for i in groups_list:
           groups[i] = self.students['merged_students'][self.students['merged_students']['Группа'] == i].reset_index(drop=True)
        return groups