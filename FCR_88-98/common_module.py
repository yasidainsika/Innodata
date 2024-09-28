import os
import re
import sys
from datetime import datetime

def ret_file_name_full(source_id, location_id, rule_name, extention):
    exe_folder = os.path.dirname(str(os.path.abspath(sys.argv[0])))
    date_prefix = datetime.today().strftime("%Y%m%d")
    out_path = os.path.join(exe_folder, 'out', remove_invalid_paths(source_id),(date_prefix), remove_invalid_paths(location_id))
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    index = 1
    outFileName = os.path.join(out_path, remove_invalid_paths(rule_name) + extention)
    retFileName = outFileName
    while os.path.isfile(retFileName):
        retFileName = os.path.join(out_path, remove_invalid_paths(rule_name)+"_"+str(index) + extention)
        index +=1
    return retFileName

def ret_out_folder(source_id, location_id):
    exe_folder = os.path.dirname(str(os.path.abspath(sys.argv[0])))
    date_prefix = datetime.today().strftime("%Y%m%d")
    out_path = os.path.join(exe_folder, 'out', remove_invalid_paths(source_id), 'Skip Rules',remove_invalid_paths(location_id),date_prefix)
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    return out_path

def return_lists(file_path):
    rules = []
    try:
        with open(file_path, 'r', encoding='utf-8') as my_file:
            read_content = my_file.read().strip()
            cleaned_read_content = re.sub(r'[^a-zA-Z0-9]+', '', read_content)
            rules=cleaned_read_content.upper()
    except FileNotFoundError:
        print("File 'links.txt' not found. Please make sure it exists.")
    return rules

def clean_rule_title(rule_name):
    cleaned_rule_name = re.sub(r'[^a-zA-Z0-9]+', '', rule_name)
    return cleaned_rule_name.strip().upper()

def shorten_rule_name(rule_name, max_length=150):
    if len(rule_name) > max_length:
        return rule_name[:max_length]
    return rule_name

def remove_invalid_paths(path_val):
    return re.sub(r'[\\/*?:"<>|]', "", path_val)

def append_error(source_id,error):
    date_prefix = datetime.today().strftime("%Y%m%d")
    exe_folder = os.path.dirname(str(os.path.abspath(sys.argv[0])))
    err_file_path = os.path.join(exe_folder, 'out', remove_invalid_paths(source_id), (date_prefix))
    if not os.path.exists(err_file_path):
        os.makedirs(err_file_path)
    err_file_path=os.path.join(err_file_path,'errors.txt')
    with open(err_file_path, "a") as myfile:
        myfile.write(str(error)+'\n')

def append_new_rule(source_id,rule_name):
    date_prefix = datetime.today().strftime("%Y%m%d")
    exe_folder = os.path.dirname(str(os.path.abspath(sys.argv[0])))
    new_rule_path = os.path.join(exe_folder, 'out', remove_invalid_paths(source_id), (date_prefix))
    if not os.path.exists(new_rule_path):
        os.makedirs(new_rule_path)
    new_rule_path=os.path.join(new_rule_path,'new_rules.txt')
    with open(new_rule_path, "a") as myfile:
        myfile.write(str(rule_name)+'\n')


