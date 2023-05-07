from os import listdir, makedirs
from os.path import join, splitext, isdir, basename
import numpy as np
import pandas as pd
import argparse
from ConfigHandler import ConfigHandler
from data_reader.DataReader import DataReader
from students_handler.StudentsHandler import StudentsHandler
from course_handler.CourseHandler import CourseHandler

parser = argparse.ArgumentParser()
    
parser.add_argument("-c", action ="store", dest='configuration_file_path', required=True,
                    help="""Путь к конфигурационному файлу с настройками""")

args = parser.parse_args()


if __name__ == '__main__':
    config_handler = ConfigHandler(args.configuration_file_path)
    students_info = config_handler.get_students_info()
    [courses_paths, courses_info] = config_handler.get_courses_info()

    students_handler = StudentsHandler(students_info)
    students = students_handler.get_student_groups()
    groups = students_handler.parse_students_into_groups()

    courses_handler = CourseHandler(courses_info, groups, students)
    courses_handled = courses_handler.handle_courses()

    