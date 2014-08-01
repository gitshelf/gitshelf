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
from cliff.app import App
from cliff.commandmanager import CommandManager
from gitshelf.version import version_info as version
import logging
import sys


class GitShelfShell(App):
    """Parent class for the 2 sub-commands."""
    log = logging.getLogger(__name__)

    def __init__(self):
        super(GitShelfShell, self).__init__(
            description='Manage a collection of git repos without using submodules',
            version=version.canonical_version_string(),
            command_manager=CommandManager('gitshelf.cli'),
        )

        self.log = logging.getLogger(__name__)

    def build_option_parser(self, description, version):
        parser = super(GitShelfShell, self).build_option_parser(description, version)

        return parser


def main():
    app = GitShelfShell()
    sys.exit(app.run(sys.argv[1:]))
