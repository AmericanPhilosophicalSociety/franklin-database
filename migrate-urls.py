# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 11:51:50 2024

@author: dnelson
"""


import requests
import csv


def load_csv(path):
    rows = []
    with open(path, 'r') as f:
        csv_reader = csv.DictReader(f)
        fieldnames = csv_reader.fieldnames
        for row in csv_reader:
            rows.append(row)

    return fieldnames, rows


def write_csv(path, data, fieldnames):
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def process_url(weight, data):
    node_id = data[weight]
    url = f'https://diglib.amphilsoc.org/node/{node_id}'
    return url


def generate_api_data(ledger):
    api = f'https://diglib.amphilsoc.org/odi-fix/{ledger}'
    r = requests.get(api)
    data = r.json()
    output = {}
    for row in data:
        output.update({row['field_weight_value']: row['nid']})
    return output
    

# mapping of ledgers to NIDs
ledgers = {
    'Ledger A': '275500',
    'Shop Book': '275668',
    'Ledger D': '275501',
    'Philadelphia [Post Office Ledger, No.2]': '275570',
    'Post Office Accounts, May 18, 1748': '275581',
    'Post Office Book, 1748-1752': '275583'
    }

in_file = 'P:\\Center for Digital Scholarship\\franklin-database\\franklin-ledgers-2024-02-21.csv'
out_file = 'P:\\Center for Digital Scholarship\\franklin-database\\franklin-ledgers-url-update.csv'

fieldnames, data = load_csv(in_file)

output = []
check = ''
for row in data:
    manu = row['source']
    if check != manu:
        pages = generate_api_data(ledgers[manu])
    if manu == 'Philadelphia [Post Office Ledger, No.2]':
        page_number = row['page_number']
    elif manu == 'Post office Book, 1748-1752':
        page_number = str(int(row['page_number'] + 2))
    else:
        page_number = row['url']
        if page_number.endswith('tif'):
            page_number = page_number.replace('tif', '')
        page_number = page_number[-3:]
        if page_number.startswith('-'):
            page_number = page_number.replace('-', '')
        page_number = page_number.lstrip('0')
    new_url = process_url(page_number, pages)
    row.update({'url': process_url(page_number, pages)})
    check = manu
    output.append(row)

write_csv(out_file, output, fieldnames)
