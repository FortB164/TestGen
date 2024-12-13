import os
import sys
import subprocess
"""
if hasattr(sys, "_MEIPASS"):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")
bat_file_path = os.path.join(base_path, "dep.bat")
if os.path.exists(bat_file_path):
    print("Running dep.bat to install dependencies...")
    subprocess.run(bat_file_path, shell=True)
else:
    print("dep.bat file not found! Dependencies may not be installed.")
"""
from TestGen import analyze_code_and_generate_tests
subprocess.run(["python", "UI.py"])
with open('programming_files_list.txt', 'r') as file:
    for line in file:
        analyze_code_and_generate_tests(line.strip())