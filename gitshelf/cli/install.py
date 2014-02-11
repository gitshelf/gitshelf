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
from sh import git
from gitshelf.cli import BaseCommand

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

            if not os.path.exists(book_path):
                LOG.info("Creating book {0} from {1}, branch: {2}".format(book_path,
                                                                          book['git'],
                                                                          book['branch']))
                git.clone(book['git'], book_path)
            else:
                LOG.info("Book {0} already exists".format(book_path))

            cwd = os.getcwd()
            os.chdir(book_path)
            cb = git("symbolic-ref", "HEAD").replace('refs/heads/', '').rstrip('\r\n')
            LOG.warn("Book {0}'s current branch is {1}".format(book_path, cb))

            if cb != book['branch']:
                LOG.info("Switching {0} from {1} to branch {2}".format(book_path,
                                                                       cb,
                                                                       book['branch']))
                git.checkout(book['branch'])

            os.chdir(cwd)
