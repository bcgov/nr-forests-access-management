import json

def read_json_file(file_path):
    with open(file_path, 'r') as myfile:
        data=myfile.read()

    # parse file
    obj = json.loads(data)
    return obj