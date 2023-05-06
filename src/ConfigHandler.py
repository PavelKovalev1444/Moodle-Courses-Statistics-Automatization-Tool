import json

class ConfigHandler(object):
    
    def __init__(self, config_file_path):
        self.config =''
        with open(config_file_path) as f:
            self.config = json.load(f)
            self.courses_info = self.config['coursesInfo']
            self.students_info = self.config['studentsInfo']
        self.process_courses_info()
        self.process_students_info()


    def process_courses_info(self):
        self.courses_paths = {}
        for i in range(len(self.courses_info)):
            course_path = self.courses_info[i]['path']
            course_name = self.courses_info[i]['shortName']
            if(course_path == ""):
                self.print_error_message("path", i, "coursesInfo")
                break
            if(course_name == ""):
                self.print_error_message("shortName", i, "coursesInfo")
                break
            self.courses_paths.setdefault(course_name, course_path)


    def process_students_info(self):
        self.students_info = self.students_info
        self.students_deans = self.students_info['studentsDeans']
        self.students_cathedra = self.students_info['studentsCathedra']


    def print_error_message(param: str, obj_number: str, obj_type: str):
        print("Error in {} {}! Wrong {} param.".format(obj_type, obj_number, param))


    def get_json(self):
      return self.config

    
    def get_courses_info(self):
        return [self.courses_paths, self.courses_info]
    

    def get_students_info(self):
        #return [self.students_deans, self.students_cathedra]
        return self.students_info