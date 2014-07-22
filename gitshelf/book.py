# Copyright 2012 Hewlett-Packard Development Company, L.P. All Rights Reserved.
#
# Author: Simon McCartney <simon.mccartney@hp.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import logging
import os
import errno
from sh import git
from gitshelf.utils import Url

LOG = logging.getLogger(__name__)


class Book:
    """ Object to represent a book - repo on disk

        Books can be one of 2 types:
            1) a git repo
            2) a symlink to another location

        Keyword arguments:
            path -- absolute or relative path to the location the repo should be in
            git -- git url to be used as the source for the repo
            branch -- branch/sha1/tag to be used in the checkout, defaults to master
            link -- destination of the link target
            skiprepourlcheck -- flag to skip that the git url matches the definition during status checks
            fakeroot -- a gitshelf may specify absolute paths, setting fakeroot allows you to make an absolute path relative to the passed path

    """

    def __init__(self,
                 book,
                 git=None,
                 branch='master',
                 link=None,
                 skiprepourlcheck=False,
                 fakeroot=None):
        """Instantiate a book object"""
        self.path = book
        self.git = git
        self.link = link
        self.branch = branch
        self.skiprepourlcheck = skiprepourlcheck
        self.fakeroot = fakeroot

        if (self.git is None) and (self.link is None):
            raise StandardError("Book is neither git or link!")

        if self.fakeroot is not None:
            LOG.debug('fakepath set, prepending {0} to {1}'.format(
                self.fakeroot, self.path))
            # need to strip any leading os.sep
            book_path = os.path.join(self.fakeroot, self.path.lstrip(os.sep))
            self.path = book_path
            LOG.debug('book.path is now {0}'.format(self.path))

    def create(self):
        if self.git and self.link is None:
            self._create_git()
        elif self.link and self.git is None:
            self._create_link()

    def _create_git(self):
        """create a book from a git repo"""

        if not os.path.exists(self.path):
            LOG.info(("Creating book {0} from {1}, branch: {2}" +
                     "").format(self.path, self.git, self.branch))
            git.clone(self.git, self.path)
        else:
            LOG.info("Book {0} already exists".format(self.path))

        cwd = os.getcwd()
        os.chdir(self.path)

        if self.skiprepourlcheck:
            remote_match_found = False
            for remote in git("remote", "-v"):
                remote_parts = remote.split()

                if Url(remote_parts[1]) == Url(self.git):
                    remote_match_found = True

            if remote_match_found:
                LOG.debug('Found {0} in the list of remotes for {1}'.format(self.git, self.path))
            else:
                LOG.error('ERROR: {0} wasn\'t found in the list of remotes for {1}'.format(self.git, self.path))

        if not self._check_branch():
            LOG.info("Switching {0} to branch {1}".format(self.path,
                                                          self.branch))
            git.fetch
            git.checkout(self.branch)

        os.chdir(cwd)

    def _create_link(self):
        """create a book from a link to somewhere else"""

        if not os.path.islink(self.path):
            LOG.info("Creating book {0} via a link to {1}".format(self.path, self.link))
            # create the parent directory, if required
            self._mkdir_p(os.path.dirname(self.path.rstrip(os.sep)))
            # create the symlink
            os.symlink(self.link, self.path)
        else:
            LOG.info("Book {0} already exists, target: {1}".format(self.path, os.readlink(self.path)))

    def _mkdir_p(self, path):
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    def _check_branch(self):
        """Check that the current working directory is at the given branch/sha1"""

        cb = git('describe', '--all', '--contains', '--abbrev=4', 'HEAD').rstrip('\r\n')
        sha1 = git('rev-parse', 'HEAD').rstrip('\r\n')
        LOG.debug("Book {0} should be at {1}".format(self.path, self.branch))
        LOG.debug("Book {0}'s current branch is {1}".format(self.path, cb))
        LOG.debug("Book {0}'s current sha1 is {1}".format(self.path, sha1))

        if ((cb == self.branch) or (sha1 == self.branch)):
            return True
        else:
            LOG.warn("WARNING {0} is at branch:{1} (sha1: {2}), not {3}".format(self.path,
                                                                                cb,
                                                                                sha1,
                                                                                self.branch))
            return False

    def status(self):
        if self.git and self.link is None:
            # git repo, check it exists & isn't dirty
            if not os.path.exists(self.path):
                LOG.info("ERROR book {0} from {1} doesn't exist.".format(
                    self.path,
                    self.git))
            else:
                # chdir to the book & run `git status`
                cwd = os.getcwd()
                os.chdir(self.path)
                if self._check_branch():
                    git_status = git.status()
                    if "nothing to commit, working directory clean" in git_status:
                        LOG.info("# book {0} OK".format(self.path))
                    else:
                        LOG.info("# book {0}".format(self.path))
                        LOG.info(git_status)
                os.chdir(cwd)

        elif self.link and self.git is None:
            # check the link points to the correct location
            link_target = os.readlink(self.path)
            LOG.debug('book: {0} should point to {1}, it points to {2}'.format(self.path, self.link, link_target))
            if link_target == self.link:
                LOG.info('# book {0} correctly points to {1}'.format(self.path, self.link))
            else:
                LOG.error('{0} should point to {1}, it points to {2}'.format(self.path, self.link, self.link))

        else:
            LOG.error('Unknown book type: {0}'.format(self.path))

    def diff(self):
        if self.git and self.link is None:
            # git repo, check it exists & isn't dirty
            if not os.path.exists(self.path):
                LOG.info("ERROR book {0} from {1} doesn't exist.".format(
                    self.path,
                    self.git))
            else:
                # chdir to the book & run `git status`
                cwd = os.getcwd()
                os.chdir(self.path)
                LOG.info("# book {0}".format(self.path))
                git_diff = git.diff()
                if git_diff:
                    LOG.info("# book {0} had changes:".format(self.path))
                    LOG.info(git_diff)
                else:
                    LOG.info("# book {0} is clean".format(self.path))
                os.chdir(cwd)
        elif self.link and self.git is None:
            # check the link points to the correct location
            link_target = os.readlink(self.path)
            LOG.debug('book: {0} should point to {1}, it points to {2}'.format(self.path, self.link, link_target))
            if link_target == self.link:
                LOG.info('# book {0} correctly points to {1}'.format(self.path, self.link))
            else:
                LOG.error('{0} should point to {1}, it points to {2}'.format(self.path, self.link, self.link))
        else:
            LOG.error('Unknown book type: {0}'.format(self.path))

    @staticmethod
    def discover(rootdir='.', usebranch=False):
        """discover all the git repo's under this directory"""
        books = []
        for root, subFolders, files in os.walk(rootdir):
            for file in files:
                this_file = os.path.join(root, file).replace(rootdir + os.sep, '')
                if this_file.endswith('.git/config') and not this_file.startswith('.git/config'):
                    repo = os.path.dirname(os.path.dirname(this_file))
                    branch = (Book._discover_branch(repo))
                    sha1 = (Book._discover_sha1(repo))
                    remotes = Book._discover_remotes(repo)
                    LOG.debug("Found a git repo! {0}".format(repo))
                    LOG.debug("remotes are {0}".format(remotes))
                    LOG.debug("branch is {0}".format(branch))
                    LOG.debug("sha1 is {0}".format(sha1))
                    if usebranch:
                        books.append(Book(book=repo, git=remotes['origin'], branch=branch))
                    else:
                        books.append(Book(book=repo, git=remotes['origin'], branch=sha1))

                if os.path.islink(this_file):
                        books.append(Book(book=this_file, link=os.readlink(this_file)))
        return books

    @staticmethod
    def _discover_branch(path='.'):
        """discover the git branch/sha1 of the given directory"""
        cwd = os.getcwd()
        os.chdir(path)
        cb = git('describe', '--all', '--contains', '--abbrev=4', 'HEAD').rstrip('\r\n')
        os.chdir(cwd)
        return cb

    @staticmethod
    def _discover_sha1(path='.'):
        """discover the git branch/sha1 of the given directory"""
        cwd = os.getcwd()
        os.chdir(path)
        sha1 = git('rev-parse', 'HEAD').rstrip('\r\n')
        os.chdir(cwd)
        return sha1

    @staticmethod
    def _discover_remotes(path='.'):
        """discover the remote repos configured for a repo"""
        cwd = os.getcwd()
        os.chdir(path)
        remotes = {}
        for remote_line in git("remote", "-v"):
            r = remote_line.split()[:2]
            remotes[r[0]] = r[1]
        os.chdir(cwd)
        return remotes

    @staticmethod
    def _discover_remote(path='.'):
        """return  the origin remote, or the first remote if origin isn't defined"""
        remotes = Book._discover_remotes(path)
        if 'origin' in remotes:
            return remotes['origin']
        else:
            return remotes[remotes.keys()[0]]
