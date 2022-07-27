<img src="pyTickLogo.png" align="right" />

# pyTick: A WIP CLI Tickspot API wrapper

pyTick allows you to load entries to the Tickspot platform

## Usage

~~~ bash
"""pyTick, A WIP CLI Tickspot API wrapper.

It is able to upload entries to Tickspot given the 
task_id and the amount of hours.

Usage:
    pyTick_cli.py [--verbose] [--version] [--help] <command> [--] [<args>...]

With command being:
    csv          Uploads hours from a csv file or stdin
    entries      Get all entries in a date range
    new          Create new entries from a file or from arguments

options:
    -h --help     Show this screen.
    -v --verbose  Show arguments.
    --version     Show version."""
~~~

To use it you need to load your credentials into a **.env** inside the script directory:

~~~ python
userAgent="app_name (sample@email.com)"
token="yourTickspotToken"
subscriptionID=999999
~~~

Your token can be get in the settings section of your account along with your subscriptionID. For your userID it is in the url of your account page.

### Examples

Upload 2.5 hours (2 hours and 30 minutes) to the task id 9999999 with the note 
'Bug crushing' for the 2012-12-11 (11 December 2012).

~~~ bash
pytick.py new 9999999 2.5 --note='Bug crushing' --date="2012-12-11"
~~~

## How does it work

It makes http requests as tick indicates in their [API documentation](https://github.com/tick/tick-api). Tick just sends and receives json. The ones i work here have a structure like this: 

![](jsonStructure.png)

**Be careful**, I added suffixes to make it more understandable. The figure mentions things like project_id but they just called id when they refer to de entity itself inside of the json file.

## Installation

1. Check you have the dependencies:

~~~ python
dotenv 1.3.4
docopt 0.6.2
pandas 1.3.4
~~~

2. Clone the repository and run the script inside of the repo directory.
CSV files uploads were tested ONLY on the script main directory, so paste them there to guarantee that it will run.