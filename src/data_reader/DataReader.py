from os import listdir, makedirs
from os.path import join, splitext, isdir, basename
import pandas as pd


class DataReader(object):
    
    def __init__(self):
        pass


    def check_extension(self, file: str, allowed_ext: str or list = 'csv') -> bool:
        file_ext = splitext(file)[1]
        if type(allowed_ext) is str:
            return file_ext == f'.{allowed_ext}'
        else:
            return file_ext in map(lambda x: f'.{x}', allowed_ext)


    def get_files(self, path: str):
        if isdir(path):
            filenames = listdir(path)
            filepaths = list(map(lambda file: join(path, file), filenames))
            files = [file for file in filepaths if self.check_extension(file, 'csv') or self.check_extension(file, 'xlsx')]
            return len(files)>0, files
        else:
            return (True, path) if self.check_extension(path, ['xlsx', 'csv']) else (False, None)


    def read_csv(self, filepath: str) -> pd.DataFrame:
        return pd.read_csv(filepath)


    def read_xlsx(self, filepath: str) -> dict:
        xl = pd.ExcelFile(filepath, engine='openpyxl')
        data = {}
        for sheet in xl.sheet_names:
            data[sheet] = pd.read_excel(filepath, sheet_name=sheet, engine='openpyxl')
        return data


    def add_file_by_name_to_dfs_dict(self, filepath: str, dfs: dict):
        file_basename = basename(filepath)
        name, ext = splitext(file_basename)
        if ext == '.csv':
            data = {name: self.read_csv(filepath)}
        else:
            data = self.read_xlsx(filepath)
        dfs.setdefault(name, data)


    def read_data(self, path: str):
        success, files = self.get_files(path)
        if success:
            dfs = {}
            if type(files) is list:
                for file in files:
                    self.add_file_by_name_to_dfs_dict(file, dfs)
            else:
                self.add_file_by_name_to_dfs_dict(files, dfs)
            return dfs
        else:
            return None