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
import re
from gitshelf.utils import NestedDict
from gitshelf.book import Book
from cliff.command import Command

LOG = logging.getLogger(__name__)


class BaseCommand(Command):
    """ Parent Command object for gitshelf """

    def get_parser(self, prog_name):
        parser = super(BaseCommand, self).get_parser(prog_name)

        parser.add_argument('--gitshelf',
                            dest='gitshelf',
                            default='gitshelf.yml',
                            nargs=1,
                            help="path to gitshelf YAML config, defaults to gitshelf.yml",
                            action='store')

        parser.add_argument('--token',
                            dest='tokens',
                            default=None,
                            nargs=1,
                            help="inject a token for substituion, overrides any environment level tokens",
                            action='append')

        parser.add_argument('--skip-deletes', help="skip and group/rule deletes", action="store_true")

        parser.add_argument('--fakeroot',
                            dest='fakeroot',
                            default=None,
                            help='path to prepand to any book paths, to test shelves '
                                 'that are absolute without using the absolute path')

        parser.add_argument('--environment',
                            dest='environment',
                            default=None,
                            nargs=1,
                            help='set the desired environment, overriding any default'
                                 'settings in the config file (gitshelf.yml)')

        parser.add_argument('--dry-run',
                            default=False,
                            help="Defaults to False",
                            action='store_true')

        parser.add_argument('--skip-repo-url-check',
                            dest='skiprepourlcheck',
                            default=False,
                            help='Defaults to False'
                                 'Skip the repo remote host check',
                            action='store_true')

        return parser

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
        config_file = parsed_args.gitshelf.pop() if isinstance(parsed_args.gitshelf, list) else parsed_args.gitshelf
        LOG.debug("config_file = {0}".format(config_file))

        with open(config_file) as fh:
            config = NestedDict(yaml.load(fh))

        with open(config_file) as fh:
            config_raw = fh.read()

        if parsed_args.environment:
            environment = parsed_args.environment[0]
        else:
            environment = config['defaults'].get('environment', 'dev')

        tokens = config['environments'][environment]['tokens']
        LOG.debug('Tokens: {0}'.format(tokens))

        # overwrite the tokens loaded from the file with any passed on the
        # command line
        if parsed_args.tokens:
            LOG.debug("Tokens have been passed on the command line: {0}".format(parsed_args.tokens))
            # split them into key/value pair, but we are passed a list of lists
            # so cli_token[0] accessess the item we want
            for cli_token in parsed_args.tokens:
                LOG.debug("Parsing the command line token: {0}".format(cli_token))
                split_token = cli_token[0].partition("=")
                LOG.debug("Split command line token: {0}".format(split_token))
                tokens[split_token[0]] = split_token[2]

            LOG.debug('Tokens: {0}'.format(tokens))

        # expand out tokens, tokens are {} wrapped names from the environment section
        delimiters = ('{', '}')

        def _replaceToken(match):
            # Strip the delimiter with 1:-1
            key = match.group(0)[1:-1]
            if key in tokens:
                return tokens[key]    # Strip the delimiter with 1:-1
            return ''

        rendered_config = re.sub('\%s.*?\%s' % delimiters, _replaceToken, config_raw)

        # reload the config block from the rendered yaml
        config = yaml.load(rendered_config)

        LOG.debug(config)

        return config

    def _get_books(self, parsed_args, config):

        LOG.debug("parsed_args: {0}".format(parsed_args))
        LOG.debug("config: {0}".format(config))

        # load the config into an array of Book objects
        books = []
        for book in config['books']:
            LOG.debug("Fresh book: {0}".format(book))
            book.update({'fakeroot': parsed_args.fakeroot})
            LOG.debug("Final book: {0}".format(book))
            # the dictionary we get from the parsed configuration should
            # match the named parameters to the Book class, so we use
            # ** to unpack the dictionary to the class arguments
            books.append(Book(**book))

        return books
