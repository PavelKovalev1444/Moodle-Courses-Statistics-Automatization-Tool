from os import listdir, makedirs
from os.path import join, splitext, isdir, basename
import pandas as pd
import numpy as np

class DataWriter(object):

    def __init__(self, groups_statistics):
        self.groups_statistics = groups_statistics


    def write_results(self, results_dir_path: str):
        for i in self.groups_statistics:
            self.make_group_document(str(i), self.groups_statistics[i], results_dir_path)


    def make_group_document(self, group, group_statistics, results_dir_path):
        if isdir(results_dir_path):
            writer = pd.ExcelWriter(f'{results_dir_path}/{group}_out.xlsx', engine='openpyxl')
            for title, course_stat in group_statistics.items():
                course_stat.to_excel(writer, sheet_name=title)
            writer.save()
        else:
            makedirs(results_dir_path)
            writer = pd.ExcelWriter(f'{results_dir_path}/{group}_out.xlsx', engine='openpyxl')
            for title, course_stat in group_statistics.items():
                course_stat.to_excel(writer, sheet_name=title)
            writer.save()