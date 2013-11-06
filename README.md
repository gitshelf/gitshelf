# gitshelf - a shelf full of git repos

Manage a collection of git repos that you don't want to manage as sub-modules

## Install

~~~
pip install gitshelf
~~~

## Usage:

### Create the required clones

~~~
$ gitshelf install
~~~

### Check for repo drift

Run `git status` against each repo, reporting drift
~~~
$ gitshelf status
~~~

