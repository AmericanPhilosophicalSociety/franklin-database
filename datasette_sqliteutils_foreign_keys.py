#python api for sqlite-utils script
# note (DRN): legacy code inherited at project start 2022-02-23
# INSTRUCTIONS AS OF AUGUST 2023: IGNORE ALL LEADING COMMENTS - CHANGE FILE NAMES TO MATCH AT THE START OF THE UNCOMMENTED CODE
# AND JUST RUN THE THING -- IT SHOULD WORK
# COMMENTED OUT STUFF, EVEN STUFF DRN WROTE, DOESN'T WORK!


#first ran the following in containing folder to create a database w everything in it (with table named transactions) using sqlite-utils CLI:
#sqlite-utils insert franklin_ledgers.db transactions Transactions_Datasette_v10.csv --csv

#now I can use python API to play with database

##from sqlite_utils import Database
##db = Database("franklin_ledgers.db")

#need to drop unnecessary (unnamed) index column
##transactions = db["transactions"]
##transactions.transform(drop={""})

#need to separate out columns from transactions that will go into accounts table
##transactions.extract(["account_id", "connected_id", "full_name", "account_geo", "account_occup"], table="accounts")

#view new table's schema
##accounts = db["accounts"]
##print(accounts.schema)

#make accounts table pk "account_id"
##accounts.transform(pk="account_id")

#that didn't work bc account_id does not pass unique paramater test
#so drop the table it made, called "accounts_new_48edc8166268"
##db["accounts_new_48edc8166268"].drop()

#rename the "account_id" column in "accounts" to "ledger_account_id"
##accounts.transform(rename={"account_id": "ledger_account_id"})

#now separate out goods_services columns
##transactions.extract(["broad_cat","narrow_cat"], table="goods_services")

#move page, page_url, source, notes_orig, notes_transcriber columns of "transactions" to the end
##transactions.transform(column_order=("rowid", "trans_id", "date", "trans_type", "accounts_id", "activity", "goods_services_id", "due_pounds", "due_shill", "due_pence","ledgerE_brot", "ledgerE_carried", "post_loc","post_wt", "gaz_no", "notes_orig","notes_transcriber", "TP", "source","page","page_url"))



#second go-round: make an "all" table that is easier to query on user end
##first ran the following in containing folder to create a database w everything in it (with table named transactions) using sqlite-utils CLI:
#sqlite-utils insert franklin_ledgers_all.db all_transactions Transactions_Datasette_v10.csv --csv

# from sqlite_utils import Database
# db = Database('franklin_ledgers_all.db')

# need to drop unnecessary columns
# code no longer necessary as raw data was restructured
# transactions = db['all_transactions']
# print('Dropping unnecessary columns...')
# transactions.transform(drop={'', 'TP', 'ledgerE_brot', 'ledgerE_carried',
#                              'notes_transcriber'})

# reordering columns
# print('Reordering columns...')
# transactions.transform(column_order=('rowid', 'trans_id', 'date', 'account_id',
#                                      'connected_id', 'full_name',
#                                     'account_geo', 'account_occup',
#                                      'trans_type', 'activity', 'broad_cat',
#                                      'narrow_cat', 'due_pounds', 'due_shill',
#                                      'due_pence', 'post_loc', 'post_wt',
#                                      'gaz_no', 'notes_orig', 'source', 'page',
#                                      'page_url'))
#
# 2022-02-23 David Nelson took over this project, all material below from him.
# create full-text search: from command line, run:
# sqlite-utils enable-fts franklin_ledgers_all.db all_transactions full_name activity notes_orig
# sqlite-utils enable-fts file-name.db table_name column_a column_b column_c column_d

# db['all_transactions'].extract(['lemay_index', 'standardized_full_name'],
#                                table='lemay_ids', fk_column='lemay_id')

# lemay_index = db['lemay_ids']

# that created a table with a new column, "id", which was the primary key
# So need to drop that column and reset primary key
# lemay_index.transform(pk='lemay_index')
# lemay_index.transform(drop={'id'})

# db['all_transactions'].add_foreign_key('lemay_id', 'lemay_ids', 'lemay_index',
#                                        ignore=True)

# Third time's the charm. The "extract" command doesn't work because it
# removes the unique IDs from the table and replaces them with an integer
# in sequential order starting from one.
# So instead, we're going to try creating a separate table from scratch for the
# foreign keys and then associating them after the fact.
# From command line, run:
# sqlite-utils insert franklin_ledgers_all.db all_transactions franklin-ledgers-full-names.csv --csv
# sqlite-utils insert franklin_ledgers_all.db lemay_ids name-index-reconciled.csv --csv

from sqlite_utils import Database
import subprocess
db = Database('franklin_ledgers_all.db')

# use subprocess to run commands from the command line without having to
# enter each one individually
command_a = ['sqlite-utils', 'insert', 'franklin_ledgers_all.db',
'all_transactions', 'franklin-ledgers-2024-02-23.csv', '--csv']
command_b = ['sqlite-utils', 'insert', 'franklin_ledgers_all.db', 'people',
'lemay-index-2023-10-13.csv', '--csv']
command_c = ['sqlite-utils', 'insert', 'franklin_ledgers_all.db',
'goods_services', 'transaction_categories.csv', '--csv']
command_d = ['sqlite-utils', 'insert', 'franklin_ledgers_all.db',
'transaction_ids', 'transaction_ids.csv', '--csv']
command_e = ['sqlite-utils', 'insert', 'franklin_ledgers_all.db',
'postal_locations', 'postal_locations.csv', '--csv']

command_list = [command_a, command_b, command_c, command_d, command_e]

for i in command_list:
    subprocess.run(i, shell=True)

# set primary key for name index
# label is detected automatically if there is an obvious name
# otherwise, label can be set in the metadata file
name_index = db['people']
name_index.transform(pk='lemay_id')

trans_cat = db['goods_services']
trans_cat.transform(pk='controlled_description')

trans_id = db['transaction_ids']
trans_id.transform(pk='transaction_id')

post_loc = db['postal_locations']
post_loc.transform(pk='postal_location')

db.add_foreign_keys([
    ('all_transactions', 'lemay_index', 'people', 'lemay_id'),
    ('all_transactions', 'controlled_description', 'goods_services',
        'controlled_description'),
    ('all_transactions', 'transaction_id', 'transaction_ids', 'transaction_id'),
    ('all_transactions', 'post_location', 'postal_locations', 'postal_location')
])

# specify certain columns as int to facilitate sorting

all_transactions = db['all_transactions']
all_transactions.transform(types={
    "pounds": int,
    "shillings": int,
    "pence": int,
    "post_weight": int
})

# configure full-text search using subprocess

search_command = ['sqlite-utils', 'enable-fts', 'franklin_ledgers_all.db',
    'all_transactions', 'full_name', 'activity', 'controlled_description',
    'narrow_description']
name_search = ['sqlite-utils', 'enable-fts', 'franklin_ledgers_all.db',
    'people', 'standardized_name', 'variant_names']

subprocess.run(search_command, shell=True)
subprocess.run(name_search, shell=True)

indexer_a = ['sqlite-utils', 'create-index', 'franklin_ledgers_all.db',
    'all_transactions', 'place', 'occupation', 'transaction_type',
    'narrow_description', 'gazette_no', 'gender', 'transaction_entered_by']
