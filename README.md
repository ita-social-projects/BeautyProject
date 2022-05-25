# Beauty project

Our project was created in order to bring customers closer to the service providers of the beauty industry.    
We are trying to improve the interaction of the main participants in these processes. The client is provided with a tool for convenient registration for the services of a hairdresser, barber and other specialists. Specialists get the opportunity to use their time more efficiently. And the owners of beauty salons will be able to attract new customers and monitor the workload of their specialists.

[![GitHub license](https://img.shields.io/github/license/ita-social-projects/BeautyProject)](https://github.com/ita-social-projects/BeautyProject/blob/master/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/ita-social-projects/BeautyProject)](https://github.com/ita-social-projects/BeautyProject/issues)
[![Pending Pull-Requests](https://img.shields.io/github/issues-pr/ita-social-projects/BeautyProject?style=flat-square)](https://github.com/ita-social-projects/BeautyProject/pulls)
[![GitHub top language](https://img.shields.io/github/languages/top/ita-social-projects/BeautyProject)](https://img.shields.io/github/languages/top/ita-social-projects/BeautyProject)

---
Content
- [Installation](#Installation)
  - [Clone](#Clone)
  - [Required to install](#Required-to-install)
  - [Environment](#Environment)
  - [How to run local](#How-to-run-local)
  - [How to run Docker](#How-to-run-Docker)
  - [Setup](#Setup)
- [Tests](#Tests)
- [Project deploy](#project-deploy)
- [Usage](#Usage)
- [Documentation](#Documentation)
- [Contributing](#contributing)
  - [Before entering](#Before-entering)
  - [Git flow](#Git-flow)
  - [Issue flow](#Issue-flow)
- [FAQ](#faq)
- [Teams](#Teams)
- [Support](#support)
- [License](#license)

----

## Installation

### Clone or Download

-  Clone this repo to your local machine using   
```
git clone https://github.com/ita-social-projects/BeautyProject.git
```
  or download the project archive: https://github.com/ita-social-projects/BeautyProject/archive/refs/heads/main.zip    

<a name="footnote">*</a> - to run the project you need an `.env` file in root folder

### Required to install

- [![Python](https://docs.python.org/3.9/_static/py.svg)](https://www.python.org/downloads/release/python-3912/) 3.9.12
- Project reqirements:
```
pip install -r /requirements.txt
```

### Environment

- Add the environment variables file (.env) to the project folder.
It must contain the following settings:
```
SECRET_KEY = '😊YOUR_SECRET_KEY😊'
DEBUG = False
ALLOWED_HOSTS = *
DB_NAME='😊YOUR_DB_NAME😊'
DB_USER='😊YOUR_DB_USER😊'
DB_PASS='😊YOUR_DB_PASS😊'
DB_HOST='😊YOUR_DB_HOST😊'
DB_PORT='😊YOUR_DB_PORT😊'
GOOGLE_API_KEY='😊YOUR_GOOGLE_API_KEY😊'
```

### How to run local

- Start the terminal.
- Go to the directory "your way to the project" / BeautyProject / beauty
- Run the following commands
```
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

### How to run Docker

- Run our project using Docker:
```
docker-compose up
```



### Setup

- Create a superuser using the terminal:    
```
python manage.py createsuperuser
```

----

## Tests

- Run project tests:
```
python manage.py test
```

----

## Project Deploy

- http://3.65.253.196/

---
## Usage

- TBC

----

## Documentation

- TBC

---

## Contributing

### Before entering

You're encouraged to contribute to our project if you've found any issues or missing functionality that you would want to see. Here you can see [the list of issues](https://github.com/ita-social-projects/BeautyProject/issues) and here you can create [a new issue](https://github.com/ita-social-projects/BeautyProject/issues/new/).

Before sending any pull request, please discuss requirements/changes to be implemented using an existing issue or by creating a new one. All pull requests should be done into [development](https://github.com/ita-social-projects/BeautyProject/) branch.

Every pull request should be linked to an issue. So if you make changes on frontend, backend or admin parts you should create an issue with a link to corresponding requirement (story, task or epic).

### Git flow

We have **[main](https://github.com/ita-social-projects/BeautyProject/tree/main)** , **[development](https://github.com/ita-social-projects/BeautyProject)** and **feature** branches.  
All **feature** branches must be merged into [development](https://github.com/ita-social-projects/BeautyProject) branch!!!
Feature branches should be named as follows `Feature/#ID_short_feature_name` (e.g. `Feature/#13_Set_up_database`)


Only the release should be merged into the main branch!!!

![Github flow](<https://wac-cdn.atlassian.com/dam/jcr:b5259cce-6245-49f2-b89b-9871f9ee3fa4/03%20(2).svg?cdnVersion=1312>)

#### Step 1


-  Clone this repo to your local machine using   
```
git clone https://github.com/ita-social-projects/BeautyProject.git
```
  or create new branch from [development](https://github.com/ita-social-projects/BeautyProject) branch


#### Step 2

- Add some commits to your new branch

#### Step 3

- Create a new pull request using <a href="https://github.com/ita-social-projects/BeautyProject/compare/" target="_blank">github.com/ita-social-projects/BeautyProject</a>.


### Issue flow

#### Step 1

- Go to [issues](https://github.com/ita-social-projects/BeautyProject/issues) and click `New issue` button

#### Step 2

- When creating an [issue](https://github.com/ita-social-projects/BeautyProject/issues/new/choose) you should add name for the issue, description, choose assignee, label, project. If issue is a `User Story` you should link it with corresponding tasks, and corresponding tasks should be linked to issue.

#### Step 3

- If issue is in work it should be placed in proper column on dashboard according to its status.

---

## FAQ

- The section will be filled as requests are received

----

## Teams

### Development team (Lv-689)
[![@Serhii-Voloshyn](https://github.com/Serhii-Voloshyn.png?size=200)](https://github.com/Serhii-Voloshyn)
[![@YaroslavBorysko](https://github.com/YaroslavBorysko.png?size=200)](https://github.com/YaroslavBorysko)
[![@Misha86/](https://github.com/Misha86.png?size=200)](https://github.com/Misha86)
[![@morento101](https://github.com/morento101.png?size=200)](https://github.com/morento101)
[![@shv833](https://github.com/shv833.png?size=200)](https://github.com/shv833)
[![@pazuzu-ua/](https://github.com/pazuzu-ua.png?size=200)](https://github.com/pazuzu-ua/)
[![@shevchenkoira](https://github.com/shevchenkoira.png?size=200)](https://github.com/shevchenkoira)
[![@therobotisnotatoy](https://github.com/therobotisnotatoy.png?size=200)](https://github.com/therobotisnotatoy)
[![@OleksiiDatsiuk](https://github.com/OleksiiDatsiuk.png?size=200)](https://github.com/OleksiiDatsiuk)

### IT Academy team
[![@kolyasalubov](https://github.com/kolyasalubov.png?size=200)](https://github.com/kolyasalubov)
[![@Deer-WarLord](https://github.com/Deer-WarLord.png?size=200)](https://github.com/Deer-WarLord)

---

## Support

- This option is currently missing. You can contact a team member directly. You can go to the team member's page in the [teams section](#Teams) by clicking on his or her avatar.

---

## License

- **[MIT license](http://opensource.org/licenses/mit-license.php)**
- Copyright 2022 © <a href="https://softserve.academy/" target="_blank"> SoftServe IT Academy</a>.

[MIT](https://choosealicense.com/licenses/mit/) 

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)