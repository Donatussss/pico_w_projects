import os

def find_file(start_path, target):
    try:
        entries = os.listdir(start_path)
    except OSError:
        return None

    for entry in entries:
        path = start_path + "/" + entry if start_path != "/" else "/" + entry
        try:
            if os.stat(path)[0] & 0x4000:  # directory
                result = find_file(path, target)
                if result:
                    return result
            else:
                if entry == target:
                    return path
        except OSError:
            pass

    return None

def path_join(*args):
    final_path = ''
    for arg in args:
        temp_path = ''
        if len(final_path) > 0:
            temp_path = f'{final_path}{"/" if final_path[-1] != "/" else ""}{arg}'
        else:
            temp_path = arg
        
        final_path = temp_path
        
    return final_path