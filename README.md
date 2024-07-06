<div align="center">
  <h1><b>DJANGO REST FRAMEWORK REPOSITORY DESIGN</b></h1>
  <h4>A base repository design for building rest api for enterprise application using django rest framework</h4>
</div>

## 📗 Table of Contents

- [📖 About the Project](#about-project)
  - Repository structure for building rest api using django rest framework.
    - [👀 Overview](#overview)
      - The repository is already integrated with postgres.
    - [🛠 Built With](#built-with)
      - Python
      - Poetry
      - Docker
      - Docker Compose
      - [🔥 Tech Stack](#tech-stack)
        - Django
        - Django Rest Framework
        - Postgres
      - [🔑 Key Features](#key-features)
        - Factory Design Pattern
        - Decorator Pattern
        - Clean Code Approach
        - Model View Controller (MVC) Design Pattern
        - SOLID Principles
- [💻 Getting Started](#getting-started)
  - [📜 Prerequisites](#prerequisites)
    - python3
    - python virtualenv
    - poetry
    - postgres
    - docker
    - docker-compose
    - git
  - [⚓ Install](#setup)
    - install the various tools listed under prerequisite on your local machine
    - for instructions on how to install and set up these tools, please check their websites for directions
  - [⚙️ Setup](#install)
    - from your terminal, navigate to your preferred directory location on your machine
    - clone the repository into a directory of your choice
    - navigate into the application's directory
  - [▶️ Run Application](#run-application)
    - without docker:
      - create a virtual environment and activate it by executing below commands
        - for linux, run
          1. `python3 -m venv venv`
          2. `source venv/bin/activate`
        - for windows, run
          1. `python3 -m venv venv`
          2. `venv\Scripts\activate`
      - with the virtual environment activated, run below commands to install dependencies
          1. `poetry install --no-root`
      - after installing dependencies, perform below actions
          1. create a file called `.env` in the root directory of the application
          2. copy the content of the file `.env.example` into  the file `.env`
          3. set the variables in the file `.env` to their appropriate values
      - after installing dependencies, run below command to start application
          1. apply database migrations to the database with command `python3 manage.py migrate`
          2. start the application with command `python3 manage.py runserver`
    - with docker:
      - build the docker image
        1. run command `docker build -t django-repo-structure:latest .`
      - start application with docker
        1. set variable `DB_HOST` in `.env` file to `backend_db`
        2. run command to start application `docker-compose up`
  - [🕹️ Usage](#usage)
    - access application on http://localhost:8000/api/docs/
    - test endpoint from swagger documentation
  - [💯 Run tests](#run-tests)
    - To run the unit tests cases
      1. run the  command `python3 manage.py test -v 2`
  - [🚀 Deployment](#triangular_flag_on_post-deployment)
    - TODO
- [👥 Author](#author)
  - Michael Asumadu
    - email ✉️ : michaelasumadu10@gmail.com
    - country 🌍 : Ghana 🇬🇭
    - phone 📞 : +233 247 049 596
