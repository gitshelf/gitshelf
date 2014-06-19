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
from gitshelf.book import Book

LOG = logging.getLogger(__name__)


class GitShelfDiscoverCommand(BaseCommand):
    """ Discover the git repos & symlinks under this directory """

    def get_parser(self, prog_name):
        parser = super(BaseCommand, self).get_parser(prog_name)
        parser.add_argument('--use-branch',
                            default=False,
                            help="Use the branch name instead of the sha1 for pinning",
                            action='store_true')
        return parser

    def execute(self, parsed_args):
        """execute, something to do for this command."""

        # get back the collection of books
        books = Book.discover(usebranch=parsed_args.use_branch)

        # sort the list, based on the path attribute
        books.sort(key=lambda book: book.path)

        # now iterate over the list of book objects
        # TODO: be less hacky and use a YAML emitter
        print "books:"
        for book in books:
            print "  - book: {0}".format(book.path)
            if book.git is not None:
                print "    git: {0}".format(book.git)
                print "    branch: {0}".format(book.branch)
            elif book.link is not None:
                print "    link: {0}".format(book.link)
            print
