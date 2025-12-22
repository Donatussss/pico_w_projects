import os
import json
from aes_utils import *
from os_utils import *

def pad_str(in_str, max_len):
    in_str_len = len(in_str)
    if in_str_len <= max_len:
        return in_str + ('0' * (max_len - in_str_len))
    return None

def get_key():
    if (key := pad_str(input('Enter key: '), 16)) is not None:
        return key
    else:
        print('Invalid key length')
        return None

def create_update_record(f_code, key, input_json):
    site_pid = input('Enter site or password identifier: ')

    if len(site_pid) == 0:
        print('Cannot have empty site or password identifier')
        return False

    if f_code == 'c':
        if site_pid in input_json.keys():
            print(f'{site_pid} record already exists')
            return False

        username_email = input('Enter username or leave blank to use email: ')
        password = encrypt_password(key, input('Enter password: '))

        input_json[site_pid] = {'username_email': username_email, 'password': password}

        return True

    elif f_code == 'u' and (res:= read_record(key, input_json, site_pid)) is not None:         
        new_username_email = input('Enter username or leave blank to leave unchanged: ')
        new_password = input('Enter password or leave blank to leave unchanged: ')

        input_json[site_pid] = {'username_email': new_username_email if len(new_username_email) > 0 else res['username_email'], 'password': encrypt_password(key, new_password) if len(new_password) > 0 else encrypt_password(key, res['password'])}

        return True
    
    return False


def delete_record(input_json):
    site_pid = input('Enter site or password identifier: ')

    if site_pid in input_json.keys():
        confirmation = input(f'Are you sure you want to delete record for {site_pid}(y/n)? ')

        if confirmation.lower() == 'y':
            del input_json[site_pid]

def read_record(key, input_json, site_pid=None):
    if site_pid is None:
        site_pid = input('Enter site or password identifier: ')

    if site_pid in input_json.keys():
        return {'username_email': input_json[site_pid]["username_email"], 'password': decrypt_password(key, input_json[site_pid]["password"])}
    
    else:
        print(f'No record found')

    return None


def email_setup(base_path=None):
    if base_path is None:
        base_path = os.getcwd()

    try:
        email = input('Enter email: ')
        store_json = None
        if not ('store' in os.listdir(base_path) and os.stat('store')[0] & 0x4000):
            os.mkdir(path_join(base_path, 'store'))
        store_json_path = find_file(path_join(base_path,'store'), f'{email}.json')

        if store_json_path:
            with open(store_json_path, 'r') as f:
                store_json = json.load(f)

        else:
            create = input(f'No store found for {email}. Create one? ')

            if create.lower() == 'y':
                store_json = {}
                store_json_path = path_join(base_path,'store',f'{email}.json')
                print(f'store_json_path: {store_json_path}')
        
        return [email, store_json, store_json_path]
    
    except Exception as e:
        print(f'Exception in {email_setup.__name__}: {e}, type: {type(e)}')

        return [None, None, None]