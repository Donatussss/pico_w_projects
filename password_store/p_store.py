import json
import os
import ubinascii
from os_utils import *
from hash_utils import *
from utils import *

auth_json = None

try:
    with open('auth.json', 'r') as f:
        auth_json = json.load(f)
except:
    print('No auth file found')


key = get_key()

if key is not None:
    # verification
    verified = False
    if auth_json is None:
        print('Storing auth credentials')
        temp = create_password(key)
        with open('auth.json', 'w') as f:
            json.dump(get_store_hash(temp), f)
        verified = True
    
    elif auth_json is not None:
        temp_json = load_stored_hash(auth_json)
        if verify_password(key, temp_json['salt'], temp_json['rounds'], temp_json['hash']):
            verified = True
        else:
            print('Verification failed')

    if verified:
        email, store_json, store_json_path = email_setup(os.getcwd())

        while store_json is not None:
            f_code = input('Enter f_code(c,d,h,l,q,r,s): ')
            
            if f_code == 'c' or f_code == 'u': # create or update
                create_update_record(f_code, key, store_json)
                with open(store_json_path, 'w') as f:
                    json.dump(store_json, f)
            elif f_code == 'd': # delete
                delete_record(store_json, f)
                with open(store_json_path, 'w') as f:
                    json.dump(store_json, f)
            elif f_code == 'h': # help 
                print('Password storage help:')
                print('c: create record')
                print('d: delete record')
                print('h: display help')
                print('l: list available records')
                print('q: quit')
                print('r: read record')
                print('s: switch email')
            elif f_code == 'l': # list
                print(f'Available site_pids: {list(store_json.keys())}')
            elif f_code == 'q': # quit
                break
            elif f_code == 'r': # read
                if (res := read_record(key, store_json)) is not None:
                    print(f'Username/email: {email if len(res["username_email"]) == 0 else res["username_email"]}')
                    print(f'Password: {res["password"]}')
            elif f_code == 's': # switch email
                email, store_json, store_json_path = email_setup(os.getcwd())


print('Reached program end')