# gitshelf - a shelf full of git repos

Manage a collection of git repos that you don't want to manage as sub-modules

Created to be used to manage a set of salt states, formula & pillars in a controlled fashion, the default config file is a YAML file that can also be loaded as a pillar (for whatever reason).
Using the branch parameter, you can pin a repo to a branch, sha1, tag, whatever you need to keep it at your known good version.

Also supports creating symlinks for you.

Other similar tools include [gilt](https://github.com/metacloud/gilt) AOSP's [repo](https://code.google.com/archive/p/git-repo/)

## Install

gitshelf is published on pypi [here](https://pypi.python.org/pypi/gitshelf), so you can install from pypi using pip:

    pip install gitshelf


You can also install from the github repo:

    pip install git+http://github.com/gitshelf/gitshelf

We use the python [sh](https://pypi.python.org/pypi/sh) sub process interface to work with git repos, so you'll need a standard git cli install, if you don't know how to do that, this might be the wrong tool for you.

## Usage

Here's a sample gitshelf.yml

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
      - book: srv/salt/pillar/base/top.sls
        link: some/link/target.sls


### Create the required clones

    $ gitshelf install

### Check for repo drift

Run `git status` against each repo, reporting drift

    $ gitshelf status

### Discover all the repos
Crudely create a gitshelf.yml for the current directory, recurses down through the directory looking for git repos (by looking for .git/config) and symlinks:

    $ gitshelf discover
    books:
      - book: srv/salt/pillar/base
        git: ssh://simonm@gerrit.paas.hpcloud.net:29418/paas-core/salt-openstack/pillar-base
        branch: 7a46de1c2b666dda2c37ee9183ef28c0a4b0f82d
      - book: srv/salt/pillar/env/someplace
        link: ../../base
      - book: srv/salt/state/base
        git: ssh://simonm@gerrit.paas.hpcloud.net:29418/paas-core/salt-openstack/state-base
        branch: dbfb89908011bb9e177dd3ceac0369e3ca884937
      - book: srv/salt/state/beaver-formula
        git: ssh://simonm@gerrit.paas.hpcloud.net:29418/paas-share/salt/beaver-formula.git
        branch: 0d00d407cef62bcc4e9a2fe8e7d5b21aebdddaa3
      - book: srv/salt/state/dbaas_state_env
        git: ssh://simonm@gerrit.paas.hpcloud.net:29418/paas-core/salt-openstack/dbaas_state_env
        branch: 9bbe4bd94951aa5c47f17efe5fedcc230551e8d1
      - book: srv/salt/state/elasticsearch-formula
        git: ssh://simonm@gerrit.paas.hpcloud.net:29418/paas-share/salt/elasticsearch-formula.git
        branch: 36252f32d48a54c598c9d52b011ec8b7625d164c
      - book: srv/salt/state/logstash-formula
        git: ssh://simonm@gerrit.paas.hpcloud.net:29418/paas-share/salt/logstash-formula.git
        branch: ef246438c2aeb7f9d934409191edd7dc1ebf904e

Or use the branch name instead of the SHA1:

    $ gitshelf discover --use-branch
    books:
      - book: srv/salt/pillar/base
        git: ssh://simonm@gerrit.paas.hpcloud.net:29418/paas-core/salt-openstack/pillar-base
        branch: ae1az1
      - book: srv/salt/pillar/env/someplace
        link: ../../base
      - book: srv/salt/state/base
        git: ssh://simonm@gerrit.paas.hpcloud.net:29418/paas-core/salt-openstack/state-base
        branch: master
      - book: srv/salt/state/beaver-formula
        git: ssh://simonm@gerrit.paas.hpcloud.net:29418/paas-share/salt/beaver-formula.git
        branch: master

### Tokens & Environments
gitshelf supports token replacement in the `gitshelf.yml`:

    defaults:
      environment: dev

    environments:
      prod:
        description: "Prod deploy kit, use the r/o git mirror"
        tokens:
          giturlbase: "https://paas-core-salt-ae1@gerrit.paas.hpcloud.net"
      dev:
        description: "dev deploy kit, use the gerrit repo"
        tokens:
          giturlbase: "ssh://simonm@gerrit.paas.hpcloud.net:29418"

    books:
      - book: "/srv/salt/state/formulae/beaver"
        git: "{giturlbase}/paas-share/salt/beaver-formula"
        branch: 'b3032ff60bbfc77472f79f621b214d0393963796'

You can specify the environment to use using the `--environment` option:

    gitshelf install --environment prod

TODO: Add support for specifying a token on the command line

## Development

pbr introduces some weirdness under virtualenv, so we use the site packages to help make
sure pbr doesn't break everything.

    virtualenv --system-site-packages .venv && . .venv/bin/activate && python setup.py develop
    # hack

## publishing a new version

build & upload to pypi in a single hit:

    git tag -s 0.0.x
    python setup.py sdist upload
