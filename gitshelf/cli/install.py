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
from cliff.command import Command

LOG = logging.getLogger(__name__)


class GitShelfInstallCommand(Command):
    """ Install a set of repos """

    def get_parser(self, prog_name):
        parser = super(GitShelfInstallCommand, self).get_parser(prog_name)

        parser.add_argument('--gitshelf',
                            dest='gitshelf',
                            default='gitshelf.yml',
                            nargs=1,
                            help="path to Gitshelf YAML config, defaults to Gitshelf",
                            action='store')

        parser.add_argument('--dry-run',
                            default=False,
                            help="Defaults to False",
                            action='store_true')

        return parser

    def execute(self, parsed_args):
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

            if not os.path.exists(book['book']):
                LOG.info("Creating book {0} from {1}, branch: {2}".format(book['book'],
                                                                          book['git'],
                                                                          book['branch']))
                git.clone(book['git'], book['book'])
            else:
                LOG.info("Book {0} already exists".format(book['book']))

            cwd = os.getcwd()
            os.chdir(book['book'])
            cb = git("symbolic-ref", "HEAD").replace('refs/heads/', '').rstrip('\r\n')
            LOG.warn("Book {0}'s current branch is {1}".format(book['book'], cb))

            if cb != book['branch']:
                LOG.info("Switching {0} from {1} to branch {2}".format(book['book'],
                                                                       cb,
                                                                       book['branch']))
                git.checkout(book['branch'])

            os.chdir(cwd)


    def post_execute(self, data):
        """ Format the results locally if needed.

        By default we just return data.

        :param data: Whatever is returned by self.execute()

        """
        return data

    def take_action(self, parsed_args):
        # TODO: Common Exception Handling Here
        results = self.execute(parsed_args)
        return self.post_execute(results)

    def _parse_configuration(self, parsed_args):
        # Read the main config file
        LOG.debug(parsed_args)
        with open(parsed_args.gitshelf) as fh:
            config = yaml.load(fh)

        LOG.debug(config)

        return config
