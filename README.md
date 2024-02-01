# Barista salary calculator
Project for managing cafe shifts with the ability to calculate barista salaries for a selected period.

## Description
This project is a barista salary calculator for a selected period. Let's say there are several cafes and several baristas. Any barista can be on shift any day in one of any cafes. A barista's earnings per day depend on the cafe's income in that day and his salary rate at that cafe. The barista has a unique salary rate for each cafe. That is, to calculate a barista’s salary for a certain period, you need to add up his earnings for all days across all cafes. The barista has three salary rate parameters by which the daily salary is calculated:

**_min_wage_** – this is the minimum daily wage that a barista get if the cafe’s income for that day is less than this parameter.

**_percent_** – this is a percentage of the cafe’s daily income for calculating the barista’s salary if the cafe’s income is higher than **_min_wage_**.

**_additive_** – this is an additional amount that is added to the barista's daily salary to compensate for the small salary if the percentage of income is less than **_min_wage_**.

## Capabilities

To access you must login. You can login as a such **_user_** or as an **_admin_**.

### User
If you are logged in as a regular **_user_**, you can view the site's home page.
![Default Home View](_screenshots/Index.png?raw=true "Index page")

Also, it is possible to see the shift schedule for the selected period:
![Default Home View](_screenshots/Shifts_U.png?raw=true "Shifts page")

### Admin

As an **_admin_**, you can fully use all the functionality.

You can add, edit or delete shifts.
![Default Home View](_screenshots/Shifts.png?raw=true "Shifts page")

You can contribute income for each day to the selected cafe.
![Default Home View](_screenshots/Cafes.png?raw=true "Cafes page")
![Default Home View](_screenshots/Income.png?raw=true "Income page")

You have the opportunity to view lists of salary rates for all baristas for all cafes.
![Default Home View](_screenshots/Baristas.png?raw=true "Baristas page")

You can select a barista and calculate his salary for the selected period.
![Default Home View](_screenshots/Calculation.png?raw=true "Calculation page")

Creating a cafe, adding a barista, adding barista salary rates are possible only from the admin panel. Adding new users is also only available from the admin panel. 

## How to use it
1. Fill out the shift schedule.
2. After the shifts are completed, the income for each day in each cafe is filled in. (_When income is entered, the system checks which barista worked that day in this cafe and, based on his salary rates, calculates his earnings for the day._)
3. To find out the salary for a barista for any period, you need to go to the barista page. The system will add up all salaries of all shifts of this barista and show the result.

###### _Note: If after the shift has passed and the income has been entered, it turns out that there was another barista on the shift. You can delete the previous shift and add another one with a different barista. In this case, the system will check the income for that day and calculate the barista's salary for that day according to his salary rates._

## Database structure
![Default Home View](_structure/Salary_calculator_structure.jpg?raw=true "DB structure")

# Setup

### 1. Clone project from GitHub to local computer.

Open the Git Bash console in the directory where you want to place the project. Run command:

    $ git clone https://github.com/VladyslavKlevanskyi/barista-salary-calculator.git

### 2. Create virtual environment

Open the project and run command:

    $ python -m venv venv
    
And then activate virtualenv:
    
a) For windows:

    $ venv\Scripts\activate
   
b) For mac:

    $ source venv/bin/activate
      

### 3. Installing project dependencies

Run command:

    $ pip install -r requirements.txt


### 4. Adding a secret key to the project

Generate a new secret key:

    $ python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

Rename `.env_sample` file to `.env`. Open it and replace `<your_secret_key>` with the key you generated before.


### 5. Creating a database

To create a database, run migrations:

    $ python manage.py migrate


### 6. Run tests

In order to make sure that the project is working correctly, run the tests with the command:

    $ python manage.py test 


### 7. Creating a superuser

To create a superuser run:

    $ python manage.py createsuperuser


### 8. Run the project

You can now run the development server:

    $ python manage.py runserver
    

### 9. Creating an admin-user

To access all pages of the site, you need to go to the admin panel and create a user with enabled the **STAFF STATUS** parameter. You also need to create a group with name - **_"admin"_** and add this user to this group.

#### _To create users who do not have admin rights and only have access to viewing the shift schedule, without the ability to change anything, you need to create users in the admin panel without enabled the **STAFF STATUS** parameter and not include them in the **"admin"** group._


Enjoy!