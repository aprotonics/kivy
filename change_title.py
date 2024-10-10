import os


path_to_files = "/home/time-traveller/Desktop/Selenium_get_titles"

file_name_to_change = path_to_files + "/" + "titles.txt"
file_name_to_change_to = path_to_files + "/" + "changed_titles.txt"

os.rename(file_name_to_change, file_name_to_change_to)
