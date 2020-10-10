# Facebook Crawler

## About this Project:
This project is a tool i'm developing to extract valuable data from Facebook pages.<br>
Since facebook is based on heavy scripting (PHP, JS, Ajax) behing the scenes, it becomes a big challenge to scrape data using only basic tools.<br>
I am writing different automated tasks in python, based on Selenium Webdriver to overcome the scraping challenges.<br>
**The Main Goal** of this project is to learn from the scripting experience for similar future tasks in different environments.

---------

## Configurations:
### 1. Setting Up Chromedriver and Environmental Variables:
Using your Operating-System of choice, the following operations **must be done** in order to run the crawler:
1. Download <a href="https://chromedriver.chromium.org/">Chromedriver</a> (make sure the downloaded version matches your browser's version).
2. Set an environmental variable named <b style="color:teal">CHROMEDRIVER</b> with the path to the driver's executable file.
3. Set an environmental variable named <b style="color:teal">CHROMEPROFILE</b> to the path where Chrome browser saves profile data.
    * Linux: */home/user/.config/google-chrome/Default*
    * Windows: *C:\Users\user\AppData\Local\Google\Chrome\User Data*

### 2. Create and Set Configuration and Pages files:
#### **configurations.json**
For easy setup, the crawler draw several configurations from a seperate JSON file named **configurations.json**, which can be setup from the following template:
```json
 {
    "data_path": "/path/to/data_folder",
    "facebook_auth": {
        "email": "facebook_account@email.com",
        "password": "accountPassword"
    },
    "page_path": "/path/to/page/file",
    "threshold_date": "Integer or ISO-Format (YYYY-MM-DD)"
}
```
* **data_path**: desired path/directory to save crawling data.
* **facebook_auth**: facebook authentication data (email and password) used by the crawler.
* **page_path**: the path/directory where **pages.json** is present.
* **threshold_date**: a string which can take either an **integer** (stating the amount of days the crawler goes back for posts) or an **ISO-Format date string** (e.g 2020-11-14) indicating an explicit date for the crawler to go back. It is recommended to set the crawler for working range of 2 to 7 days.

#### **pages.json**
The Crawler is scanning this page for the desired Facebook pages, and collects the available data based on additional configurations. It is necessary to set this file and the path to it's folder inside the configuration file. Please use the following template:
```json
[
    {
        "fullname": "Page #1 Display Name",
        "username": "Page1.Username"
    },
    {
        "fullname": "Page #2 Display Name",
        "username": "Page2Username"
    },
    {
        "fullname": "Page #3 Display Name",
        "username": "UserNameOfPage.3"
    }
]
```
* **fullname**: the name of the page to be displayed in exported data (can be anything the user desires, as long there are **no special characters**).
* **username**: the page's username in Facebook, can be easly extracted from the url if you navigate to the page (e.g. https://facebook.com/UserName)

---------

## Running the Crawler
After all the setup is made, simply run the main file (`python main.py`). <br>for debugging, a log file is been created at the crawling session's folder.

---------

### Important Disclaimer:
This project is open-source and written for **educational purposes only!** scraping from websites may go against the site's policy and terms of service.
I am not taking ant responsibilty for anyone who wishes to use my code for any other uses besides the learning experience.
