# Description

This project is for monitoring olx offers lists specified by input url with search queryname. See .config.example file for the example usage.
This is a little messy Python code (written in 3h). 

# Important notices
This is tested only on polish versions of portals like olx, otomoto, otodom

# Version
This code needs at least Python 3.6 because it uses f-strings.

# Start project 
Before starting the project you need to fill required variables. 
1. Create .env file based on provided example .env.example
2. Update persistent/searchconfig.yaml according to your needs

## Option 1
Install docker and docker-compose and run:
```
docker-compose up
```

## Option 2
1. create virtualenv
```
pyton3 -m venv .venv
```

2. source to the virtualenv
```
source .venv/bin/active
```

3. start the project
```
cd src
python3 main.py
```