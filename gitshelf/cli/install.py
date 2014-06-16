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

LOG = logging.getLogger(__name__)


class GitShelfInstallCommand(BaseCommand):
    """ Install a set of repos """

    def execute(self, parsed_args):
        """execute, something to do for this command."""
        # load the configuration from yaml, rendering
        # any tokens along the way
        config = self._parse_configuration(parsed_args)

        # get back the collection of books
        books = self._get_books(parsed_args, config)

        # now iterate over the list of book objects
        for book in books:
            book.create()
