from os import listdir, makedirs
from os.path import join, splitext, isdir, basename
import numpy as np
import pandas as pd
import argparse
from ConfigHandler import ConfigHandler


parser = argparse.ArgumentParser()
    
parser.add_argument("-c", action ="store", dest='configuration_file_path', required=True,
                    help="""Путь к конфигурационному файлу с настройками""")

args = parser.parse_args()


if __name__ == '__main__':
    config_handler = ConfigHandler(args.configuration_file_path)
    