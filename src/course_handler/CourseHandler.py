from data_reader.DataReader import DataReader

class CourseHandler(object):
    
    def __init__(self, coursesInfo, groups, students):
        self.groups = groups
        self.students = students
        self.coursesInfo = coursesInfo
        self.coursesNames = self.read_courses_names()
        self.read_courses()


    def read_courses_names(self):
        coursesNames = []
        for i in self.coursesInfo:
            coursesNames.append(i["shortName"])
        return coursesNames


    def read_courses(self):
        self.courses = {}
        data_reader = DataReader()
        for i in self.coursesInfo:
            current_course_dict_dict = data_reader.read_data(i["path"])
            current_course_dict = list(current_course_dict_dict.items())[:][0][1]
            course = list(current_course_dict.items())[:][0][1]
            self.courses[i["shortName"]] = course

    
    def handle_courses(self):
        self.drop_unused_columns()
        self.merge_courses_and_students()
        self.rate_students()
        return self.courses


    def drop_unused_columns(self):
        for i in self.coursesInfo:
            columns_to_drop = []
            for col in self.courses[i["shortName"]].columns:
                isIn = False
                for fixed_col in i["fixedColumns"]:
                  if (col.lower()).find(fixed_col.lower()) != -1:
                      isIn = True
                if isIn == False:
                  columns_to_drop.append(col)
            self.courses[i["shortName"]].drop(columns_to_drop, inplace=True, axis=1)
            self.courses[i["shortName"]].rename(columns=i["renameSettings"], inplace=True)
            '''
            if "email" in self.courses[i["shortName"]].columns:
                self.courses[i["shortName"]]["email"] = self.courses[i["shortName"]]["email"].str.strip()
                self.courses[i["shortName"]]["email"] = self.courses[i["shortName"]]["email"].str.lower()
            if "github" in self.courses[i["shortName"]].columns:
                self.courses[i["shortName"]]["github"] = self.courses[i["shortName"]]["github"].str.strip()
                self.courses[i["shortName"]]["github"] = self.courses[i["shortName"]]["github"].str.lower()
            '''
            self.courses[i["shortName"]][i["mergeByColumn"]] = self.courses[i["shortName"]][i["mergeByColumn"]].str.strip()
            self.courses[i["shortName"]][i["mergeByColumn"]] = self.courses[i["shortName"]][i["mergeByColumn"]].str.lower()
                

    def merge_courses_and_students(self):
        for i in self.coursesInfo:
            self.courses[i["shortName"]] = self.students.merge(
                self.courses[i["shortName"]], 
                how='left', 
                left_on=i["mergeByColumn"], 
                right_on=i["mergeByColumn"]
            )
            self.drop_y_duplicates(self.courses[i["shortName"]])
            self.rename_x_columns(self.courses[i["shortName"]])

    
    def drop_y_duplicates(self, course):
        columns_to_drop = []
        for i in course.columns:
            if i.find('_y') != -1:
                columns_to_drop.append(i)
        course.drop(columns_to_drop, inplace=True, axis=1)

    
    def rename_x_columns(self, course):
        columns_to_rename = {}
        for i in course.columns:
            if i.find('_x') != -1:
                columns_to_rename[i] = i[:-2]
        course.rename(columns=columns_to_rename, inplace=True)


    def rate_students(self):
        for i in self.coursesInfo:
            max_points_sum = 0
            for j in i["tasksInfo"]:
                max_points_sum += self.count_tasks(self.courses[i["shortName"]], j["column"], j["maxMark"])
    


    def count_tasks(self, course, task_name, task_max_mark):
        if task_max_mark == "":
            tasks_num = 0
            for i in course.columns:
                if i.find(task_name) != -1:
                    tasks_num += self.find_max_in_column(course[i].to_numpy())
            return tasks_num
        else:
            tasks_num = 0
            for i in course.columns:
                if i.find(task_name) != -1:
                    tasks_num += 1
            return tasks_num * int(task_max_mark)
        
    
    def find_max_in_column(self, col):
        max = 0
        for i in range(len(col)):
            if type(col[i]) == int:
                if col[i] > max:
                    max = col[i]
        return max
