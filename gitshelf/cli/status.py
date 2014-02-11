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
from sh import git
from gitshelf.cli import BaseCommand

LOG = logging.getLogger(__name__)


class GitShelfStatusCommand(BaseCommand):
    """ Install a set of repos."""

    def execute(self, parsed_args):
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

