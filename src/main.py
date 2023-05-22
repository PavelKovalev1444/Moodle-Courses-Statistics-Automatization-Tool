from os import listdir, makedirs
from os.path import join, splitext, isdir, basename
import numpy as np
import pandas as pd
import argparse
from ConfigHandler import ConfigHandler
from data_reader.DataReader import DataReader
from students_handler.StudentsHandler import StudentsHandler
from course_handler.CourseHandler import CourseHandler
from data_writer.DataWriter import DataWriter

import time
from memory_profiler import profile

parser = argparse.ArgumentParser()
    
parser.add_argument("-c", action ="store", dest='configuration_file_path', required=True,
                    help="""Путь к конфигурационному файлу с настройками""")

args = parser.parse_args()

@profile
def main_program():
    #time_start = time.time()
    config_handler = ConfigHandler(args.configuration_file_path)
    students_info = config_handler.get_students_info()
    [courses_paths, courses_info] = config_handler.get_courses_info()

    students_handler = StudentsHandler(students_info)
    students = students_handler.get_student_groups()
    groups = students_handler.parse_students_into_groups()

    courses_handler = CourseHandler(courses_info, groups, students)
    courses_handled = courses_handler.handle_courses()

    data_writer = DataWriter(courses_handled)
    data_writer.write_results("./results_2023")
    #time_end = time.time()
    #print('time_start = ' + str(time_start))
    #print('time_end = ' + str(time_end))
    #print('time_end - time_start = ' + str(time_end - time_start))


if __name__ == '__main__':
    main_program()