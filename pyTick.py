#!/usr/bin/env python
"""pyTick, A WIP CLI Tickspot API wrapper.

It is able to upload entries to Tickspot given the 
task_id and the amount of hours.

Usage:
    pyTick.py [--verbose] [--version] [--help] <command> [--] [<args>...]

With command being:
    csv          Uploads hours from a csv file or stdin
    entries      Get all entries in a date range
    new          Create new entries from a file or from arguments

options:
    -h --help     Show this screen.
    -v --verbose  Show arguments.
    --version     Show version."""
from subprocess import call
from docopt import docopt

if __name__ == '__main__':

    args = docopt(__doc__, version="pyTick 0.1", options_first=True)
    
    if args['--verbose']:
        print('global arguments:')
        print(args)
        print('command arguments:')

    argv = [args['<command>']] + args['<args>']
    if args['<command>'] in 'csv new entries'.split():
        # For the rest we'll just keep DRY:
        exit(call(['python', 'pytick_%s.py' % args['<command>']] + argv))
    elif args['<command>'] in ['help', None]:
        exit(call(['python', 'pytick.py', '--help']))
    else:
        exit("%r is not a pytick.py command. See 'pytick help'." % args['<command>'])
