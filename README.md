## About

This is a Python 3 command line program for writing and viewing a personal diary. It uses a simple plain text file format to store entries locally. You can view and search entries and print wordcount statistics.

This is a personal project of mine. It has undergone many iterations. I use it every day and can vouch for its stability. Feedback and pull requests are welcome. I have ideas for new features to add but unfortunately this project is no longer a high priority for me so it may take a while. 

## Dependencies

- Python 3.2+
- (Optional) [python-dateutil](https://labix.org/python-dateutil), for smarter date parsing

## How to use

Download the source code and place it anywhere you like. Run the `rundiary` script to start the program. 

Data is stored in `~/.diary/` by default. This can be changed by launching the program with the `--base` option and specifying a different directory. 

You may want to create an alias in your `.bashrc`. For example:

    alias diary='~/path/to/script/diary/rundiary -b ~/path/to/data'

## Examples

Functionality is split into multiple commands. Use `rundiary -h` to view a help message or `rundiary COMMAND -h` to get help on a specific command. 

### New

    rundiary new

Open Vim on a new entry with the date of right now.

    rundiary new --editor nano

Open `nano` on a new entry (or any other text editor).

    rundiary new -d '21 Oct 2014' -m 'Hello world'

Create a new entry with the date 21 October 2014 and the content "Hello world".

### Edit

    rundiary edit

Open Vim to edit the most recent entry.

    rundiary edit 1413881692-david-x220

Open Vim to edit the entry with ID equal to `1413881692-david-x220`. The ID can be found on the upper right of the header bar for an entry when viewing them with the `list` command.

### List/search

    rundiary list

Display entries in a never-ending list from newest to oldest. Entries will have a coloured header at the top with their *wordcount*, *date* and *ID*.

    rundiary list --asc --after 2013-10-11

Display entries in ascending date order which occurred after 11 October 2013.

    rundiary list --pipe-to cat

Pipe entries to `cat` instead of `less` (thus printing them to the terminal). You can substitute any command here. 

    rundiary search 'hello world'

Display entries containing the string 'hello world'. Also accepts any other options supported by `list`.

    rundiary search hello world

Display entries containing both the strings 'hello' and 'world' (in any order/position).

    rundiary search 'hello|world'

Display entries containing either the word 'hello' or the word 'world'.

### Wordcount

    rundiary wordcount

Print the total number of words and entries in your diary.

    rundiary wc --month

Print the number of words and entries by calendar month. Also try `--year`, `--day` or `--weekday`. You can also combine with the `--before`, `--after`, `--asc` and `--desc` syntax from the `list` command.

### Generate

    rundiary generate

Generate a set of static HTML pages in `$base_dir/html/` representing your diary. Text will be converted using Markdown. This is an *experimental feature*. 
