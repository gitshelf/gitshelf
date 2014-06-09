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
from gitshelf.cli import BaseCommand
from book import Book

LOG = logging.getLogger(__name__)


class GitShelfInstallCommand(BaseCommand):
    """ Install a set of repos """

    def execute(self, parsed_args):
        """execute, something to do for this command."""
        LOG.debug(parsed_args.__dict__)
        config = self._parse_configuration(parsed_args)

        LOG.debug(config['books'])
        # load the config into an array of Book objects
        books = []
        for book in config['books']:
            LOG.debug(book)
            # the dictionary we get from the parsed configuration should
            # match the named parameters to the Book class, so we use
            # ** to unpack the dictionary to the class arguments
            books.append(Book(**book))

        # now iterate over the list of book objects
        for book in books:
            book.install()
