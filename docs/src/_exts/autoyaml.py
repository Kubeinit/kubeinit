#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Copyright kubeinit contributors.

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.

MIT License

Copyright (c) 2021 Jakub Pieńkowski
Original from: https://github.com/Jakski/sphinxcontrib-autoyaml
"""

import os

from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.statemachine import ViewList

from ruamel.yaml.main import compose_all
from ruamel.yaml.nodes import (
    MappingNode,
    ScalarNode,
)

from sphinx.errors import ExtensionError
from sphinx.util import logging
from sphinx.util.docutils import switch_source_input


logger = logging.getLogger(__name__)


class TreeNode:
    """Tree node class."""

    def __init__(self, value, comments, parent=None):
        """Init method."""
        self.value = value
        self.parent = parent
        self.children = []
        self.comments = comments
        if value is None:
            self.comment = None
        else:
            # Flow-style entries may attempt to incorrectly reuse comments
            self.comment = self.comments.pop(value.start_mark.line + 1, None)

    def add_child(self, value):
        """Add child."""
        node = TreeNode(value, self.comments, self)
        self.children.append(node)
        return node

    def remove_child(self):
        """Remove child."""
        return self.children.pop(0)


class AutoYAMLException(ExtensionError):
    """Main plugin exception class."""

    category = 'AutoYAML error'


class AutoYAMLDirective(Directive):
    """Main plugin class."""

    required_arguments = 1

    def run(self):
        """Run the plugin."""
        self.config = self.state.document.settings.env.config
        self.env = self.state.document.settings.env
        self.record_dependencies = \
            self.state.document.settings.record_dependencies
        output_nodes = []
        location = os.path.normpath(
            os.path.join(self.env.srcdir,
                         self.config.autoyaml_root
                         + '/' + self.arguments[0]))
        if os.path.exists(location):
            print("This path exists")
        else:
            raise AutoYAMLException('location "%s" does not exists.' % (
                                    location))
        if os.path.isfile(location):
            logger.debug('[autoyaml] parsing file: %s', location)
            try:
                output_nodes.extend(self._parse_file(location))
            except Exception as e:
                print('Override')
                print(e)
                # TODO:FIXME
                pass
                # raise AutoYAMLException('Failed to parse YAML file: %s' % (location)) from e
        else:
            raise AutoYAMLException('%s:%s: location "%s" is not a file.' % (
                                    self.env.doc2path(self.env.docname, None),
                                    self.content_offset - 1,
                                    location))
        self.record_dependencies.add(location)
        return output_nodes

    def _get_comments(self, source, source_file):
        comments = {}
        in_docstring = False
        for linenum, line in enumerate(source.splitlines(), start=1):
            line = line.lstrip()
            if line.startswith(self.config.autoyaml_doc_delimiter):
                in_docstring = True
                comment = ViewList()
            elif line.startswith(self.config.autoyaml_comment) \
                    and in_docstring:
                line = line[len(self.config.autoyaml_comment):]
                # strip preceding whitespace
                if line and line[0] == ' ':
                    line = line[1:]
                comment.append(line, source_file, linenum)
            elif in_docstring:
                comments[linenum] = comment
                in_docstring = False
        return comments

    def _parse_document(self, doc, comments):
        tree = TreeNode(None, comments)
        if not isinstance(doc, MappingNode):
            return tree
        unvisited = [(doc, 0)]
        while len(unvisited) > 0:
            node, index = unvisited[-1]
            if index == len(node.value):
                if tree.parent is not None:
                    tree = tree.parent
                unvisited.pop()
                continue
            for key, value in node.value[index:]:
                index += 1
                unvisited[-1] = (node, index)
                if not isinstance(key, ScalarNode):
                    continue
                subtree = tree.add_child(key)
                if isinstance(value, MappingNode) and (
                    len(unvisited) + 1 <= self.config.autoyaml_level
                    or self.config.autoyaml_level == 0
                ):
                    unvisited.append((value, 0))
                    tree = subtree
                    break
        return tree

    def _generate_documentation(self, tree):
        unvisited = [tree]
        while len(unvisited) > 0:
            node = unvisited[-1]
            if len(node.children) > 0:
                unvisited.append(node.remove_child())
                continue
            if node.parent is None or node.comment is None:
                unvisited.pop()
                continue
            with switch_source_input(self.state, node.comment):
                definition = nodes.definition()
                if isinstance(node.comment, ViewList):
                    self.state.nested_parse(node.comment, 0, definition)
                else:
                    definition += node.comment
                node.comment = nodes.definition_list_item(
                    '',
                    nodes.term('', node.value.value),
                    definition,
                )
                if node.parent.comment is None:
                    node.parent.comment = nodes.definition_list()
                elif not isinstance(
                        node.parent.comment,
                        nodes.definition_list):
                    with switch_source_input(self.state, node.parent.comment):
                        dlist = nodes.definition_list()
                        self.state.nested_parse(node.parent.comment, 0, dlist)
                        node.parent.comment = dlist
                node.parent.comment += node.comment
            unvisited.pop()
        return tree.comment

    def _parse_file(self, source_file):
        with open(source_file, 'r') as f:
            source = f.read()
        comments = self._get_comments(source, source_file)
        for doc in compose_all(source):
            docs = self._generate_documentation(
                self._parse_document(doc, comments)
            )
            if docs is not None:
                yield docs


def setup(app):
    """Configure the plugin."""
    app.add_directive('autoyaml', AutoYAMLDirective)
    app.add_config_value('autoyaml_root', '..', 'env')
    app.add_config_value('autoyaml_doc_delimiter', '###', 'env')
    app.add_config_value('autoyaml_comment', '#', 'env')
    app.add_config_value('autoyaml_level', 1, 'env')
