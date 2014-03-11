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
import yaml
import os
import errno
from sh import git
from gitshelf.cli import BaseCommand
from gitshelf.utils import Url


LOG = logging.getLogger(__name__)


class GitShelfInstallCommand(BaseCommand):
    """ Install a set of repos """

    def take_action(self, parsed_args):
        """excute, something to do for this command."""
        LOG.debug(parsed_args.__dict__)
        config = self._parse_configuration(parsed_args)

        # iterate over the config, doing things
        books = config['books']
        LOG.debug(books)
        for book in books:
            LOG.debug(book)
            if 'branch' not in book:
                book['branch'] = 'master'

            book_path = book['book']
            if parsed_args.fakeroot:
                fakeroot = parsed_args.fakeroot[0]
                LOG.debug('fakepath set, prepending {0} to {1}'.format(fakeroot, book['book']))
                # need to strip any leading os.sep
                book_path = os.path.join(fakeroot, book_path.lstrip(os.sep))
                LOG.debug('book_path is now {0}'.format(book_path))

            if 'git' in book:
                self._book_git(book_path, book)
            elif 'link' in book:
                self._book_link(book_path, book)
            else:
                LOG.error('book {0} is of unknown type: {1}'.format(book['book'], book))

    def _book_git(self, book_path, book):
        """create a book from a git repo"""

        if not os.path.exists(book_path):
            LOG.info("Creating book {0} from {1}, branch: {2}".format(book_path,
                                                                      book['git'],
                                                                      book['branch']))
            git.clone(book['git'], book_path)
        else:
            LOG.info("Book {0} already exists".format(book_path))

        cwd = os.getcwd()
        os.chdir(book_path)
        # TODO: check that the git repo points to the same URL
        remote_match_found = False
        for remote in git("remote", "-v"):
            remote_parts = remote.split()

            if Url(remote_parts[1]) == Url(book['git']):
                remote_match_found = True

        if remote_match_found:
            LOG.debug('Found {0} in the list of remotes for {1}'.format(book['git'], book_path))
        else:
            LOG.error('ERROR: {0} wasn\'t found in the list of remotes for {1}'.format(book['git'], book_path))

        # check the branch is set as we expect
        cb = git("symbolic-ref", "HEAD").replace('refs/heads/', '').rstrip('\r\n')
        LOG.warn("Book {0}'s current branch is {1}".format(book_path, cb))

        if cb != book['branch']:
            LOG.info("Switching {0} from {1} to branch {2}".format(book_path,
                                                                   cb,
                                                                   book['branch']))
            git.checkout(book['branch'])

        os.chdir(cwd)

    def _book_link(self, book_path, book):
        """create a book from a link to somewhere else"""

        if not os.path.islink(book_path):
            LOG.info("Creating book {0} via a link to {1}".format(book_path, book['link']))
            # create the parent directory, if required
            self._mkdir_p(os.path.dirname(book_path.rstrip(os.sep)))
            # create the symlink
            os.symlink(book['link'], book_path)
        else:
            LOG.info("Book {0} already exists, target: {1}".format(book_path, os.readlink(book_path)))


    def _mkdir_p(self, path):
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise

