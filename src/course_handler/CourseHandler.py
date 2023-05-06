from data_reader.DataReader import DataReader

class CourseHandler(object):
    
    def __init__(self, courses_paths, coursesInfo, groups, students):
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
            print(self.courses[i["shortName"]].columns)
            