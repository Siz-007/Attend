import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import csv
import datetime
import shutil
import os

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "" ,
    'storageBucket': ""
})

bucket = storage.bucket()
source_file = 'attendence.csv'

current_datetime = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
destination_file = f'Current{current_datetime}.csv'

shutil.copyfile(source_file, destination_file)
with open(source_file, 'r') as source_csv:
    reader = csv.reader(source_csv)
    rows = list(reader)

# Modify the content of the destination file
# For example, you can add a header row
header_row = ['Column1', 'Column2', 'Column3']
rows.insert(0, header_row)

# Write the modified content to the destination file
with open(destination_file, 'w', newline='') as destination_csv:
    writer = csv.writer(destination_csv)
    writer.writerows(rows)

blob = bucket.blob(destination_file)
blob.upload_from_filename(destination_file)

os.remove(destination_file)


