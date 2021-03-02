from selenium import webdriver
import PyPDF2
import time
import os
import re
import pdfplumber
import json
import datetime
from collections import namedtuple
from selenium.webdriver.common.keys import Keys

def remove_existing_files(file_zero_path, file_one_path, file_two_path):
    if os.path.exists(file_zero_path):
        os.remove(file_zero_path)
    if os.path.exists(file_one_path):
        os.remove(file_one_path)
    if os.path.exists(file_two_path):
        os.remove(file_two_path)

def get_rosters(file_zero_path, file_one_path, file_two_path):
    options = webdriver.ChromeOptions()
    options.add_experimental_option('prefs', {
    "download.default_directory": "C:\\Users\\zacbr\\Documents\\20-21 Projects\\MicroServices\\Roster to Calendar\\rosters", #Change default directory for downloads
    "download.prompt_for_download": False, #To auto download the file
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
    })
    options.add_argument("--headless")
    options.add_argument("--window-size=1920x1080")
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(options=options)

    file = open("login.txt" , "r")

    content = file.readlines()

    user = content[0]
    pas = content[1]

    driver.get("https://wowpeople.woolworths.com.au/content/Login.html/")
    window_before = driver.window_handles[0]
    driver.find_element_by_id("customBtn").click()
    time.sleep(2)

    window_after = driver.window_handles[1]
    driver.switch_to.window(window_after)
    driver.find_element_by_id("Email").send_keys(user)

    time.sleep(2)
    driver.find_elements_by_class_name("mCAa0e")[0].send_keys(pas)
    driver.find_elements_by_class_name("mCAa0e")[0].send_keys(Keys.ENTER)
    driver.switch_to.window(window_before)
    time.sleep(5)

    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd':'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': 'C:\\Users\\zacbr\\Documents\\20-21 Projects\\MicroServices\\Roster to Calendar\\rosters'}}
    driver.execute("send_command", params)

    driver.get("https://wowpeople.woolworths.com.au/content/dam/wowPeoplePortal/Rosters/wow_eroster/3108_week_0.pdf")
    driver.get("https://wowpeople.woolworths.com.au/content/dam/wowPeoplePortal/Rosters/wow_eroster/3108_week_1.pdf")
    driver.get("https://wowpeople.woolworths.com.au/content/dam/wowPeoplePortal/Rosters/wow_eroster/3108_week_2.pdf")

    if not(os.path.exists(file_zero_path)):
        time.sleep(5)
    if not(os.path.exists(file_one_path)):
        time.sleep(5)
    if not(os.path.exists(file_two_path)):
        time.sleep(5)
    time.sleep(5)

    driver.quit()

def solve(s):
    if(len(s) == 5):
        s = '0' + s
    hour = int(s[:2]) % 12
    minutes = int(s[3:5])
    if s[5] == 'P':
        hour += 12
    return "{:02}:{:02}".format(hour, minutes)

def getStartTime(time):
    x = time.split(' - ')
    start = x[0]
    return solve(start)

def getEndTime(time):
    x = time.split(' - ')
    end = x[1]
    return solve(end)

def read_from_pdf(file):
    tables = []

    with pdfplumber.open(file) as pdf:
        pages = pdf.pages
        for page in pdf.pages:
            tables.append(page.extract_table(table_settings={
                "vertical_strategy": "text", 
                "horizontal_strategy": "text",
                "explicit_vertical_lines": [],
                "explicit_horizontal_lines": [],
                "snap_tolerance": 3,
                "join_tolerance": 3,
                "edge_min_length": 3,
                "min_words_vertical": 3,
                "min_words_horizontal": 1,
                "keep_blank_chars": False,
                "text_tolerance": 3,
                "text_x_tolerance": None,
                "text_y_tolerance": None,
                "intersection_tolerance": 3,
                "intersection_x_tolerance": None,
                "intersection_y_tolerance": None,
            })) 


    for x in range(6 ,15):
        if tables[x][5][0] == "Brydon, Zac":
            tables[x][4].pop(0)
            tables[x][4].pop(0)
            tables[x][5].pop(0)
            tables[x][5].pop(0)
            tables[x][6].pop(0)
            tables[x][6].pop(0)
            breaks = []
            shifts = []
            for i in range(0,7):
                if "PAID" in tables[x][6][i]:
                    break_length = "15"
                elif "30" in tables[x][6][i]:
                    break_length = "30"
                elif "60" in tables[x][6][i]:
                    break_length = "60"
                else:
                    break_length = 0
                breaks.append(break_length)
                if not(tables[x][5][i] == ''):
                    shift = {
                        "date" : datetime.datetime.strptime(tables[x][4][i], "%d/%m/%Y").strftime("%Y-%m-%d") ,
                        "startTime": getStartTime(tables[x][5][i]),
                        "endTime" : getEndTime(tables[x][5][i]),
                        "break" :break_length
                    }                 
                    shifts.append(shift)
            return shifts
            break

def main():
    file_zero_path = "C:\\Users\\zacbr\\Documents\\20-21 Projects\\MicroServices\\Roster to Calendar\\rosters\\3108_week_0.pdf"
    file_one_path = "C:\\Users\\zacbr\\Documents\\20-21 Projects\\MicroServices\\Roster to Calendar\\rosters\\3108_week_1.pdf"
    file_two_path ="C:\\Users\\zacbr\\Documents\\20-21 Projects\\MicroServices\\Roster to Calendar\\rosters\\3108_week_2.pdf"

    output_file_path = 'newShifts.json'

    remove_existing_files(file_zero_path, file_one_path, file_two_path)

    get_rosters(file_zero_path, file_one_path, file_two_path)

    file_zero = 'rosters\\3108_week_0.pdf'
    file_one = 'rosters\\3108_week_1.pdf'
    file_two = 'rosters\\3108_week_2.pdf'

    shifts = []

    week_zero = read_from_pdf(file_zero)
    week_one = read_from_pdf(file_one)
    week_two = read_from_pdf(file_two)

    for i in range (0, len(week_zero)):
        shifts.append(week_zero[i])
    for i in range (0,len(week_one)):
        shifts.append(week_one[i])
    for i in range (0, len(week_two)):
        shifts.append(week_two[i])

    f = open(output_file_path , "w")
    f.write(json.dumps(shifts))
    f.close()

if __name__ == "__main__":
    main()

