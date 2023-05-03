# Author: Abdul-Hameed Ahmed
# DESCRIPTION
# This script will pull Bridge Learning Management Training Data and route to Postgres instance via AWS
# END OF DESCRIPTION

from config import base_url, payload, headers, file_name, psql_string
from zipfile import ZipFile
import requests
import time
import pandas as pd
import urllib.parse
from sqlalchemy import create_engine
import os

def main():
    generate_data_dump()
    if check_data_dump():
        get_download()
        extract_download()
        psql_dumps()
        remove_files()
    else:
        print("Download not ready! Try again later.")

    
def generate_data_dump():
    generated_data = requests.post(base_url, json=payload, headers=headers)
    if generated_data.status_code != 201:
        raise ValueError(f"Expected 201 response, but got {generated_data.status_code}")

    print(generated_data)
    print(generated_data.url)
    print(generated_data.content)
    print(generated_data.text)


def check_data_dump():
    data_dump = requests.get(base_url, headers=headers)
    if data_dump.status_code == 200:
        while data_dump.json()["data_dumps"][0]["status"] != "complete":
            data_dump = requests.get(base_url, headers=headers)

            time.sleep(5)
            print("Download not ready yet. Waiting...")
        return True


def get_download():
    with requests.get(f"{base_url}/download", headers=headers, stream=True) as download_file:
        download_file.raise_for_status()
        with open(file_name, 'wb') as local_file:
            for chunk in download_file.iter_content():
                if chunk:
                    local_file.write(chunk)
        return file_name


def extract_download():
    with ZipFile(file_name, 'r') as zip:
        zip.printdir()
        zip.extractall(path='./temp')
        print("Extaction complete...\n")


def psql_dumps():
    engine = create_engine(psql_string)

    list_of_CSVfiles = ["object1.csv", "object2.csv", "object3.csv", "object4.csv", "object5.csv"]
    list_of_SQLtables = ["object1", "object2", "object3", "object4", "object5"]

    for csvfile, sqltable in zip(list_of_CSVfiles, list_of_SQLtables):
        print(f"Current csv file: {csvfile}")
        print(f"Current sql table: {sqltable}")

        custom_csv_df = pd.read_csv(f"./temp/{csvfile}")
        try:
            custom_csv_df.to_sql(sqltable, engine, if_exists='replace', index='false', chunksize=20000)
            print(f"Data dropped for {csvfile} to {sqltable} in postgres successful!\n\n")
        except Exception as err:
            print(f"An exception as occurred: {err}")

def remove_files():
    dir = './temp'
    for files in os.listdir(dir):
        os.remove(os.path.join(dir, files))

    print("All files are now removed from temp directory...")

    current_zip = file_name
    os.remove(current_zip)
    print("zip file removed...")


if __name__ == "__main__":
    main()
