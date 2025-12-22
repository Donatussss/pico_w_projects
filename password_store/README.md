# Password Store
A simple storage script for storing passwords on the Pico 2(2W)

## General Flow
- Authorization
  - At the start a key is required. The hash of this key will be stored. The plaintext will only last for the lifetime of the program.
  - This key will also be used for the AES encryption and decryption
- Main loop
  - This starts with an email prompt. A new email will lead to a new json file store request
  - You can:
    - c: create a record
    - d: delete a record
    - h: display help
    - l: list available records
    - q: quit
    - r: read a record
    - s: switch email