from data_reader.DataReader import DataReader

import pandas as pd
import numpy as np

class CourseHandler(object):
    
    def __init__(self, coursesInfo, groups, students):
        self.groups = groups
        self.students = students
        self.coursesInfo = coursesInfo
        self.coursesNames = self.read_courses_names()
        self.read_courses()

    
    def handle_courses(self):
        self.drop_unused_columns()
        self.merge_courses_and_students()
        self.rate_students()
        self.merge_all_students_with_courses()
        return self.group_courses_lists


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
            self.handle_single_course(self.courses[i["shortName"]], max_points_sum, i["maxMark"], i["tasksInfo"])


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


    def handle_single_course(self, course, max_sum, max_mark, tasksInfo):
        tasks_index = -1
        for i in range(len(course.columns)):
            for j in tasksInfo:
                if course.columns[i].find(j["column"]) != -1:
                    tasks_index = i
                    break
            if tasks_index != -1:
                break
        tasks_dataframe = pd.DataFrame(
            data=course[course.columns[tasks_index:]].values, 
            columns=course.columns[tasks_index:]
        )
        total, marks = self.count_total_points(tasks_dataframe.to_numpy(), max_sum, max_mark)
        course.insert(tasks_index, 'Итого', total)
        course.insert(tasks_index + 1, 'Оценка', marks)
        self.drop_tasks_columns(course, tasksInfo)
    

    def count_total_points(self, tasks_dataframe, max_sum, max_mark):
        total = []
        marks = []
        for i in range(tasks_dataframe.shape[0]):
            student_points_sum = 0
            student_mark = 0
            for j in range(tasks_dataframe.shape[1]):
                if type(tasks_dataframe[i][j]) == int:
                    student_points_sum += tasks_dataframe[i][j]
            student_mark = np.floor((student_points_sum / max_sum) * max_mark)
            total.append(student_points_sum)
            marks.append(student_mark)
        return [total, marks]
            

    def drop_tasks_columns(self, course, tasksInfo):
        columns_to_drop = []
        for i in course.columns:
            for j in tasksInfo:
                if i.find(j["column"]) != -1:
                    columns_to_drop.append(i)
        course.drop(columns_to_drop, inplace=True, axis=1)


    def merge_all_students_with_courses(self):
        self.group_courses_lists = {}
        for group in self.groups:
            self.group_courses_lists[group] = {}
            for i in self.coursesInfo:
                self.group_courses_lists[group][i["sheetName"]] = self.groups[group].merge(
                    self.courses[i["shortName"]],
                    how='left', 
                    left_on=i["mergeByColumn"], 
                    right_on=i["mergeByColumn"]
                )
                self.drop_y_duplicates(self.group_courses_lists[group][i["sheetName"]])
                self.rename_x_columns(self.group_courses_lists[group][i["sheetName"]])