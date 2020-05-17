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


def standardize_dates(input_list: list) -> None:
    for j in range(0, len(input_list)):
        input_list[j] = input_list[j].replace('Mon', 'Monday')
        input_list[j] = input_list[j].replace('Tue', 'Tuesday')
        input_list[j] = input_list[j].replace('Wed', 'Wednesday')
        input_list[j] = input_list[j].replace('Thu', 'Thursday')
        input_list[j] = input_list[j].replace('Fri', 'Friday')


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


def submit_times_from_file(web_driver_wait: WebDriverWait, file: str = 'default', skip_days: list = None) -> None:
    if not skip_days:
        skip_days = list()

    schedule_config = json_config.connect(join(dirname(__file__), '..', 'config', 'schedules', file + '.json'))

    # Cycle through the dropdown and accept hours worked for unentered weekdays
    elems = web_driver_wait.until(expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, '#date > option')))
    for i in range(0, len(elems)):
        elem = web_driver_wait.until(expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, '#date > option')))[i]
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
            web_driver_wait.until(expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '#startTime > option[value="' + start_time + '"]'))).click()
            web_driver_wait.until(expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '#endTime > option[value="' + end_time + '"]'))).click()

            # Add time
            web_driver_wait.until(expected_conditions.presence_of_element_located((By.ID, 'timeSaveOrAddId'))).click()

            # So long as we're not on the last element, head back to the "add time" page to loop through again
            if elems[-1] != elem:
                web_driver_wait.until(expected_conditions.presence_of_element_located((By.ID, 'addTime'))).click()


def get_password_from_terminal(config, prompt: str = 'eServices Password:') -> str:
    if config['password_prompt_fallback']:
        return input(prompt)

    return getpass.getpass(prompt=prompt)


def main() -> None:
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

    web_driver_wait = WebDriverWait(browser, float(config['webdriver']['timeout']) if config['webdriver']['timeout'] else 2)

    # MNSU eServices
    browser.get(config['eservices']['url'])

    # Login
    elem = web_driver_wait.until(expected_conditions.presence_of_element_located((By.ID, 'userName')))
    username = config['eservices']['username'] if config['eservices']['username'] else input('eServices Username:')
    elem.send_keys(username)
    elem = web_driver_wait.until(expected_conditions.presence_of_element_located((By.ID, 'password')))
    pwd = config['eservices']['password'] if config['eservices']['password'] else get_password_from_terminal(config)
    elem.send_keys(pwd + Keys.RETURN)

    web_driver_wait.until(expected_conditions.title_contains('Student Employment'))

    # Days where time has already been entered, so we don't go over them again (wasting time)
    days_entered = list()

    try:
        elems = web_driver_wait.until(expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, 'tbody > tr')))
    except selenium_exceptions.TimeoutException:
        # if no time has been entered, selenium will timeout searching for elements
        elems = list()

    for elem in elems:
        txt = elem.find_element_by_css_selector('td').text
        if txt != 'Total Hours':
            days_entered.append(txt)

    standardize_dates(days_entered)

    # Go to the "add time" page
    elem = web_driver_wait.until(expected_conditions.presence_of_element_located((By.ID, 'addTime')))
    elem.click()

    specific_file = input('Load from specific file? (empty for default.json, '
                                    'specify the filename without json extension):')

    if not specific_file:
        submit_times_from_file(web_driver_wait, skip_days=days_entered)
    else:
        submit_times_from_file(web_driver_wait, specific_file, days_entered)

    browser.quit()


if __name__ == '__main__':
    main()
