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
from gitshelf.cli import base

LOG = logging.getLogger(__name__)


class GitShelfStatusCommand(base.Command):
    """ Install a set of repos."""

    def get_parser(self, prog_name):
        parser = super(GitShelfStatusCommand, self).get_parser(prog_name)

        # parser.add_argument('--skip-deletes', help="skip and group/rule deletes", action="store_true")

        return parser

    def execute(self, parsed_args):
        config = self._parse_configuration(parsed_args)

        LOG.info('TODO')
        LOG.warn('TODO MOFO')
