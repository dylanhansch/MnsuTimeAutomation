import getpass
import json_config
from os.path import dirname, join
from selenium import webdriver
from selenium.common import exceptions as selenium_exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import sys

config = json_config.connect(join(dirname(__file__), '..', 'config', 'config.json'))

webdriver_driver = str.lower(config['webdriver']['driver'] or '')
webdriver_path = config['webdriver']['path']

if not webdriver_path:
    print('Config Error: You must specify a valid webdriver path.')
    sys.exit(1)

if webdriver_driver == 'chrome':
    browser = webdriver.Chrome(executable_path=webdriver_path)
elif webdriver_driver == 'firefox':
    browser = webdriver.Firefox(executable_path=webdriver_path)
elif webdriver_driver == 'edge':
    browser = webdriver.Edge(executable_path=webdriver_path)
elif webdriver_driver == 'ie':
    browser = webdriver.Ie(executable_path=webdriver_path)
elif webdriver_driver == 'safari':
    browser = webdriver.Safari(executable_path=webdriver_path)
elif webdriver_driver == 'opera':
    browser = webdriver.Opera(executable_path=webdriver_path)
elif webdriver_driver == 'phantomjs':
    browser = webdriver.PhantomJS(executable_path=webdriver_path)
elif webdriver_driver == 'webkitgtk':
    browser = webdriver.WebKitGTK(executable_path=webdriver_path)
else:
    print('Config Error: You must specify a valid supported webdriver. '
          'Options: chrome, firefox, edge, ie, safari, opera, phantomjs, webkitgtk')
    sys.exit(1)

wait = WebDriverWait(browser, float(config['webdriver']['timeout']) if config['webdriver']['timeout'] else 2)


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


def load_times_from_file(file: str = 'default', skip_days: list = None) -> None:
    if not skip_days:
        skip_days = list()

    schedule_config = json_config.connect(join(dirname(__file__), '..', 'config', 'schedules', file + '.json'))

    # Cycle through the dropdown and accept hours worked for unentered weekdays
    elems = wait.until(expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, '#date > option')))
    for i in range(0, elems.__len__()):
        elem = wait.until(expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, '#date > option')))[i]
        date_text = elem.text

        # Day from the date (date_text)
        day = detect_day(date_text)

        # Time must not already be entered in eServices
        if date_text not in skip_days:
            if not schedule_config[day] or schedule_config[day] == -1:
                continue

            start_time = schedule_config[day]['start']
            end_time = schedule_config[day]['end']

            # Select the day
            elem.click()

            # Set the times
            wait.until(expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '#startTime > option[value="' + start_time + '"]'))).click()
            wait.until(expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '#endTime > option[value="' + end_time + '"]'))).click()

            # Add time
            wait.until(expected_conditions.presence_of_element_located((By.ID, 'timeSaveOrAddId'))).click()

            # So long as we're not on the last element, head back to the "add time" page to loop through again
            if elems[-1] != elem:
                wait.until(expected_conditions.presence_of_element_located((By.ID, 'addTime'))).click()


def get_password_from_terminal(prompt: str = 'eServices Password:') -> str:
    if config['password_prompt_fallback']:
        return input(prompt)

    return getpass.getpass(prompt=prompt)


def main() -> None:
    # MNSU eServices
    browser.get(config['eservices']['url'])

    # Login
    elem = wait.until(expected_conditions.presence_of_element_located((By.ID, 'userName')))
    username = config['eservices']['username'] if config['eservices']['username'] else input('eServices Username:')
    elem.send_keys(username)
    elem = wait.until(expected_conditions.presence_of_element_located((By.ID, 'password')))
    pwd = config['eservices']['password'] if config['eservices']['password'] else get_password_from_terminal()
    elem.send_keys(pwd + Keys.RETURN)

    wait.until(expected_conditions.title_contains('Student Employment'))

    # Days where time has already been entered, so we don't go over them again (wasting time)
    days_entered = list()

    try:
        elems = wait.until(expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, 'tbody > tr')))
    except selenium_exceptions.TimeoutException:
        # if no time has been entered, selenium will timeout searching for elements
        elems = list()

    for elem in elems:
        txt = elem.find_element_by_css_selector('td').text
        if txt != 'Total Hours':
            days_entered.append(txt)

    days_entered = standardize_dates(days_entered)

    # Go to the "add time" page
    elem = wait.until(expected_conditions.presence_of_element_located((By.ID, 'addTime')))
    elem.click()

    load_from_specific_file = input('Load from specific file? (empty for default.json, '
                                    'specify the filename without json extension):')

    if not load_from_specific_file:
        load_times_from_file(skip_days=days_entered)
    else:
        load_times_from_file(load_from_specific_file, days_entered)

    browser.quit()


if __name__ == '__main__':
    main()
