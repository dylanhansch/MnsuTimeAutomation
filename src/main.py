import json_config
from os.path import dirname, join
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

config = json_config.connect(join(dirname(__file__), '..', 'config', 'config.json'))

browser = webdriver.Chrome(config['chromedriver_path'])


def standardize_dates(input_list: list) -> list:
    output_list = input_list

    for j in range(0, output_list.__len__()):
        output_list[j] = output_list[j].replace('Mon', 'Monday')
        output_list[j] = output_list[j].replace('Tue', 'Tuesday')
        output_list[j] = output_list[j].replace('Wed', 'Wednesday')
        output_list[j] = output_list[j].replace('Thu', 'Thursday')
        output_list[j] = output_list[j].replace('Fri', 'Friday')

    return output_list


# Example input_string: Wednesday, Sep 4
def detect_day(input_string: str) -> str:
    day = ''
    if 'Sunday' in input_string:
        day = 'sunday'
    elif 'Monday' in input_string:
        day = 'monday'
    elif 'Tuesday' in input_string:
        day = 'tuesday'
    elif 'Wednesday' in input_string:
        day = 'wednesday'
    elif 'Thursday' in input_string:
        day = 'thursday'
    elif 'Friday' in input_string:
        day = 'friday'
    elif 'Saturday' in input_string:
        day = 'saturday'

    return day


def load_times_from_file(file: str = 'default') -> None:
    schedule_config = json_config.connect(join(dirname(__file__), '..', 'config', 'schedules', file + '.json'))

    # Cycle through the dropdown and accept hours worked for unentered weekdays
    elems = browser.find_elements_by_css_selector('#date > option')
    for i in range(0, elems.__len__()):
        elem = browser.find_elements_by_css_selector('#date > option')[i]
        date_text = elem.text

        # Day from the date (date_text)
        day = detect_day(date_text)

        # Time must not already be entered in eServices
        if date_text not in days_entered:
            if not schedule_config[day] or schedule_config[day] == -1:
                continue

            start_time = schedule_config[day]['start']
            end_time = schedule_config[day]['end']

            # Select the day
            elem.click()

            # Set the times
            browser.find_element_by_css_selector('#startTime > option[value="' + start_time + '"]').click()
            browser.find_element_by_css_selector('#endTime > option[value="' + end_time + '"]').click()

            # Add time
            browser.find_element_by_id('timeSaveOrAddId').click()

            # So long as we're not on the last element, head back to the "add time" page to loop through again
            if elems[-1] != elem:
                elem2 = browser.find_element_by_id('addTime')
                elem2.click()


# MNSU eServices
browser.get(config['eservices']['url'])

# Login
elem = browser.find_element_by_id('userName')
username = config['eservices']['username'] if config['eservices']['username'] else input('eServices Username:')
elem.send_keys(username)
elem = browser.find_element_by_id('password')
pwd = config['eservices']['password'] if config['eservices']['password'] else input('eServices Password:')
elem.send_keys(pwd + Keys.RETURN)

# Days where time has already been entered, so we don't go over them again (wasting time)
days_entered = list()

elems = browser.find_elements_by_css_selector('tbody > tr')
for elem in elems:
    txt = elem.find_element_by_css_selector('td').text
    if txt != 'Total Hours':
        days_entered.append(txt)

    continue


days_entered = standardize_dates(days_entered)

# Go to the "add time" page
elem = browser.find_element_by_id('addTime')
elem.click()

load_from_default_file = input('Load from specific file? (empty for default.json, '
                               'specify the filename without json extension):')

if not load_from_default_file:
    load_times_from_file()
else:
    load_times_from_file(load_from_default_file)

browser.quit()
