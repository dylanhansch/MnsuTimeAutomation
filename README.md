# MnsuTimeAutomation
MNSU eServices time entry is painfully tedious and takes quite a bit of time to complete every pay cycle. This script automates the majority of the process so it takes roughly 5% as much time to get time entered.

# Installation
1. Install pipenv if you don't already have it
2. Install dependencies. From the project root run: `pipenv install`
3. Install the selenium chromedriver somewhere on your system
4. Rename config.dist.json to config.json
5. Update the absolute path to the chromedriver in config.json
6. Add your eservices username in config.json
7. Update any other values as needed in config.json
8. Update the default schedule config or create a new schedule config if needed

# Running
You can run this multiple different ways. The most common are from the IDE or the terminal.

For the terminal `cd` to the project root and run `pipenv shell`. This will launch a subshell with the virtual environment loaded. From there you can execute the main.py script as you normally would.

# Contributing
If you would like to contribute please make your changes in a descriptively named branch and open a pull request outlining your changes. If you're looking for ideas for how you can contribute check out the GitHub issues! Thanks for your interest!

# Bugs / Feature Requests
Please report bugs or request features by either opening a GitHub issue or emailing [dylan@dylanhansch.net](mailto:dylan@dylanhansch.net).
