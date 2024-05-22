#!/usr/bin/env python3

import os
import sys
import sqlite3
import glob
import time

output_db_path = "pkg.db"
table_name = "files"
src_files_glob = "pkg/**"



if len(sys.argv) > 1 and sys.argv[1] == "read":
    file_id = int(sys.argv[2])
    assert os.path.exists(output_db_path), f"error: missing input file: {output_db_path}"
    # benchmark random read access
    t1 = time.time()
    connection = sqlite3.connect(output_db_path)
    cursor = connection.cursor()
    query = f"select path, content from {table_name} where id = ?"
    args = (file_id,)
    path, content = cursor.execute(query, args).fetchone()
    t2 = time.time()
    print(f"extracted file {path} ({repr(content[0:10])}...) in {t2-t1} seconds")
    connection.close()
    sys.exit()



print("output_db_path", repr(output_db_path))
assert os.path.exists(output_db_path) == False, f"error: output exists: {output_db_path}"
os.makedirs(os.path.dirname(output_db_path) or ".", exist_ok=True)

connection = sqlite3.connect(output_db_path)
cursor = connection.cursor()

sqlite_page_size = 2**12 # 4096 = 4K = default
cursor.executescript(f"PRAGMA page_size = {sqlite_page_size}; VACUUM;")

cursor.execute("PRAGMA count_changes=OFF")

cursor.execute(
    f"CREATE TABLE {table_name} (\n"
    f"  id INTEGER PRIMARY KEY,\n"
    f"  path TEXT,\n"
    f"  content BLOB\n"
    f")"
)

file_id = -1

for path in glob.glob(src_files_glob, recursive=True, include_hidden=True):
    if not os.path.isfile(path):
        continue
    file_id += 1
    query = f"insert into {table_name} (path, content) values (?, ?)"
    with open(path, "rb") as f:
        content = f.read()
    args = (path, content)
    cursor.execute(query, args)

last_file_id = file_id

connection.commit()
connection.close()
print(f"done {output_db_path} -- last_file_id is {last_file_id}")
