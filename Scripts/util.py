import gzip
import os
import json

#create a folder in the given directory (path)
#returns True if folder already exists in directory; return False otherwise
def create_folder(path, folder_name):
    os.chdir(path)
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        return False
    else:
        #print('the folder '+folder_name+' already exists\n')
        return True

def write_json(filename, dict):
    with open(filename, 'w') as outfile:
        json.dump(dict, outfile)
    return
    
def write_json_l_gz(filename, arr_of_dict):
    with gzip.open(filename, 'wt') as outfile:
        for dict in arr_of_dict:
            json_object = json.dumps(dict, ensure_ascii=False)
            outfile.write(json_object + '\n')
