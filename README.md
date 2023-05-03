# BridgeLMS_Automation
The objective of this script is to connect to the Bridge Learning Management Training API and pull the training data on a weekly basis and route the data to a Postgres Instance via AWS.  
The pipeline setup was via GitLab running via Azure Kubernetes Service.

The script written in Python is composed of several key functions:
- generate_data_dump
- check_data_dump
- get_download
- extract_download
- psql_dumps

## generate_data_dump
```python
def generate_data_dump():
    generated_data = requests.post(base_url, json=payload, headers=headers)
    if generated_data.status_code != 201:
        raise ValueError(f"Expected 201 response, but got {generated_data.status_code}")
```
This function starts the process of making the **HTTP Post request** to your **"Bridge Base URL"** with your provided payload (selected objects you want to pull information on).  
The reason this function is **called first during the main function execution is that a post request must be made to Bridge Learning Management Training API to prepare the Data Export.**  
If a different status code over than 201 is produced then raise a ValueError message. 

## check_data_dump
```python
def check_data_dump():
    data_dump = requests.get(base_url, headers=headers)
    if data_dump.status_code == 200:
        while data_dump.json()["data_dumps"][0]["status"] != "complete":
            data_dump = requests.get(base_url, headers=headers)

            time.sleep(5)
            print("Download not ready yet. Waiting...")
        return True
```
This function makes the **HTTP get request** using your **"Bridge Base URL"**. The sleep method is there to provide a five second delay to give the API enough time to prepare the data dump zip file based on the objects added in the payload provided in the config file. 

## get_download
```python
def get_download():
    with requests.get(f"{base_url}/download", headers=headers, stream=True) as download_file:
        download_file.raise_for_status()
        with open(file_name, 'wb') as local_file:
            for chunk in download_file.iter_content():
                if chunk:
                    local_file.write(chunk)
        return file_name
```
This function proceeds with downloading the data dump zip file provided from the request made to the API. 

## extract_download
```python
def extract_download():
    with ZipFile(file_name, 'r') as zip:
        zip.printdir()
        zip.extractall(path='./temp')
        print("Extaction complete...\n")
```
This function proceeds with extracting the zip file provided from the ***get_download()*** function. 

## psql_dumps
```python
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
```
This function proceeds to take the files extracted from the zip (In this case, it's csv files) and proceeds to loop through two lists simultaneously (file name and specific table name matchup).  
During the loop the **csv file is read into a Pandas DataFrame and the pushed into the selected postgres table in AWS.**
