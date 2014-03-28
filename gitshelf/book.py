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
    """ Object to represent a book - repo on disk """

    def __init__(self, name, path, git=None, branch='master', link=None, skiprepourlcheck=False):
        """Instantiate a book object"""
        self.name = name
        self.path = path
        self.git = git
        self.link = link
        self.branch = branch
        self.skiprepourlcheck = skiprepourlcheck

        if self.git is None & self.link is None:
            raise StandardError("Book is neither git or link!")

    def _create_git(self):
        """create a book from a git repo"""

        if not os.path.exists(self.path):
            LOG.info(("Creating book {0} from {1}, branch: {2}" +
                     "").format(self.path, book['git'], book['branch']))
            git.clone(book['git'], self.path)
        else:
            LOG.info("Book {0} already exists".format(self.path))

        cwd = os.getcwd()
        os.chdir(self.path)

        if self.skiprepourlcheck:
            remote_match_found = False
            for remote in git("remote", "-v"):
                remote_parts = remote.split()

                if Url(remote_parts[1]) == Url(book['git']):
                    remote_match_found = True

            if remote_match_found:
                LOG.debug('Found {0} in the list of remotes for {1}'.format(book['git'], self.path))
            else:
                LOG.error('ERROR: {0} wasn\'t found in the list of remotes for {1}'.format(book['git'], self.path))

        # check the branch is set as we expect
        # cb = git("symbolic-ref", "HEAD").replace('refs/heads/', '').rstrip('\r\n')
        cb = git('describe', '--all', '--contains', '--abbrev=4', 'HEAD').rstrip('\r\n')
        sha1 = git('rev-parse', 'HEAD').rstrip('\r\n')
        LOG.warn("Book {0}'s current branch is {1}".format(self.path, cb))
        LOG.warn("Book {0}'s current sha1 is {1}".format(self.path, sha1))

        if ((cb != book['branch']) or (sha1 != book['branch'])):
            LOG.info("Switching {0} from {1} to branch {2}".format(self.path,
                                                                   cb,
                                                                   book['branch']))
            git.fetch
            git.checkout(book['branch'])

        os.chdir(cwd)

    def _book_link(self, self.path, book):
        """create a book from a link to somewhere else"""

        if not os.path.islink(self.path):
            LOG.info("Creating book {0} via a link to {1}".format(self.path, book['link']))
            # create the parent directory, if required
            self._mkdir_p(os.path.dirname(self.path.rstrip(os.sep)))
            # create the symlink
            os.symlink(book['link'], self.path)
        else:
            LOG.info("Book {0} already exists, target: {1}".format(self.path, os.readlink(self.path)))


    def _mkdir_p(self, path):
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise

    def status(self):
        LOG.debug(parsed_args.__dict__)
        config = self._parse_configuration(parsed_args)

        # iterate over the config, doing things
        books = config['books']
        LOG.debug(books)
        for book in books:
            LOG.debug(book)
            if 'branch' not in book:
                book['branch'] = 'master'

            self.path = book['book']
            if parsed_args.fakeroot:
                fakeroot = parsed_args.fakeroot[0]
                LOG.debug('fakepath set, prepending {0} to {1}'.format(fakeroot, book['book']))
                # need to strip any leading os.sep
                book_path = os.path.join(fakeroot, book_path.lstrip(os.sep))
                LOG.debug('book_path is now {0}'.format(book_path))

            if 'git' in book:
                if not os.path.exists(book_path):
                    LOG.info("ERROR book {0} from {1}, branch: {2} doesn't exist.".format(book_path,
                                                                              book['git'],
                                                                              book['branch']))
                else:
                    # chdir to the book & run `git status`
                    cwd = os.getcwd()
                    os.chdir(book_path)
                    LOG.info("# book {0}".format(book_path))
                    LOG.info(git.status())
                    os.chdir(cwd)

            elif 'link' in book:
                # check the link points to the correct location
                link_target = os.readlink(book_path)
                LOG.debug('book: {0} should point to {1}, it points to {2}'.format(book_path, book['link'], link_target))
                if link_target == book['link']:
                    LOG.info('# book {0} correctly points to {1}'.format(book_path, link_target))
                else:
                    LOG.error('{0} should point to {1}, it points to {2}'.format(book_path, book['link'], link_target))
            else:
                LOG.error('Unknown book type: {0}'.format(book))
