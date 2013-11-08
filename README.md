# gitshelf - a shelf full of git repos

Manage a collection of git repos that you don't want to manage as sub-modules

Created to be used to manage a set of salt states, formula & pillars in a controlled fashion, the default config file is a YAML file that can also be loaded as a pillar (for whatever reason).
Using the branch parameter, you can pin a repo to a branch, sha1, tag, whatever you need to keep it at your known good version.

## Install

We use pygit2 to work with git repos, this required libgit2

Ubuntu:  apt-get install libgit2 (or something)
OSX: brew install libgit2 (0.19 or newer)
~~~
pip install gitshelf
~~~

## Usage

Here's a sample gitshelf.yml
~~~
books:
  - book: "srv/salt/state/base"
    git: "ssh://deploy-user@internal-git-repo-server/salt/state-base"
  - book: "srv/salt/state/sudoers-formula"
    git: "https://github.com/saltstack-formulas/sudoers-formula.git"
#
# Pillars, an example of using a specific branch
  - book: "srv/salt/pillar/base"
    git: "ssh://deploy-user@internal-git-repo-server/salt/pillar-base"
    branch: "staging"
~~~
### Create the required clones

~~~
$ gitshelf install
~~~

### TODO: Check for repo drift

Run `git status` against each repo, reporting drift
~~~
$ gitshelf status
~~~

## Development

~~~
virtualenv .venv
. .venv/bin/activate
python setup.py develop
# hack
~~~
