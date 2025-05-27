- After clonning this code, you must go to requirements.txt and uncomment the pandas
- After that, you must run the following command to install all the dependencies:

```bash
pip install -r requirements.txt
```

- After that, you must run the following command to install playwright:

```bash
playwright install chromium
```

- After that, you must run the following command to install playwright:

```bash
playwright install
```

- Then you have to run convert script to convert csv to json

```bash
python convert_csv_to_json.py
```

- Then you must split urls by running this file:

```bash
python split_links_interactive.py
```

- Note that when you run split file you will be asked some questions like
- start index (e.g. 1)
- end index (e.g. 100)
- chunk size (Select how many urls you want to scrape in one container)

- Then you've to build docker image and run it by running this command
  - Note that you can duplicated containers services like if you have 15 chunks then you've to create 15 containers you can do it by editing compose file go to gpt and ask it i want to duplicate this service 15 times and then copy and paste it after that you must run this command below:

```bash
docker compose up --build
```

This command will first build the image and then scrap the data
