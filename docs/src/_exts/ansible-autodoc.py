#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Copyright 2019 Red Hat, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
"""

import imp
import os

from docutils import core
from docutils import nodes
from docutils.parsers import rst
from docutils.parsers.rst import Directive
from docutils.writers.html4css1 import Writer

from ruamel.yaml import YAML as RYAML

try:
    import io
    StringIO = io.StringIO
except ImportError:
    import StringIO


class DocYaml(RYAML):
    """Main class for YAML processing."""

    def _license_filter(self, data):
        """Filter out our boilerplate license heading in return data.

        The filter is used to allow documentation we're creating in variable
        files to be rendered more beautifully.
        """
        lines = list()
        mark = True
        for line in data.splitlines():
            if '# Copyright' in line:
                mark = False
            if mark:
                lines.append(line)
            if '# under the License' in line:
                mark = True
        return '\n'.join(lines)

    def dump(self, data, stream=None, **kw):
        """Dump stream data."""
        if not stream:
            stream = StringIO()
        try:
            RYAML.dump(self, data, stream, **kw)
            return self._license_filter(stream.getvalue().strip())
        finally:
            stream.close()


DOCYAML = DocYaml()
DOCYAML.default_flow_style = False


class AnsibleAutoPluginDirective(Directive):
    """Main class for the plugin directive."""

    directive_name = "ansibleautoplugin"
    has_content = True
    option_spec = {
        'module': rst.directives.unchanged,
        'role': rst.directives.unchanged,
        'documentation': rst.directives.unchanged,
        'examples': rst.directives.unchanged
    }

    @staticmethod
    def _render_html(source):
        return core.publish_parts(
            source=source,
            writer=Writer(),
            writer_name='html',
            settings_overrides={'no_system_messages': True}
        )

    def make_node(self, title, contents, content_type=None):
        """Make a documentation node."""
        section = self._section_block(title=title)
        if not content_type:
            # Doc section
            for content in contents['docs']:
                for paragraph in content.split('\n'):
                    retnode = nodes.paragraph()
                    retnode.append(self._raw_html_block(data=paragraph))
                    section.append(retnode)

            # Options Section
            options_list = nodes.field_list()
            options_section = self._section_block(title='Options')
            for key, value in contents['options'].items():
                options_list.append(
                    self._raw_fields(
                        data=value['description'],
                        field_name=key
                    )
                )
            else:
                options_section.append(options_list)
                section.append(options_section)

            # Authors Section
            authors_list = nodes.field_list()
            authors_list.append(
                self._raw_fields(
                    data=contents['author']
                )
            )
            authors_section = self._section_block(title='Authors')
            authors_section.append(authors_list)
            section.append(authors_section)

        elif content_type == 'yaml':
            for content in contents:
                section.append(
                    self._literal_block(
                        data=content,
                        dump_data=False
                    )
                )
        return section

    @staticmethod
    def load_module(filename):
        """Load the module."""
        return imp.load_source('__ansible_module__', filename)

    @staticmethod
    def build_documentation(module):
        """Build the documentation."""
        docs = DOCYAML.load(module.DOCUMENTATION)
        doc_data = dict()
        doc_data['docs'] = docs['description']
        doc_data['author'] = docs.get('author', list())
        doc_data['options'] = docs.get('options', dict())
        return doc_data

    @staticmethod
    def build_examples(module):
        """Build the examples."""
        examples = DOCYAML.load(module.EXAMPLES)
        return_examples = list()
        for example in examples:
            return_examples.append(DOCYAML.dump([example]))
        return return_examples

    def _raw_html_block(self, data):
        html = self._render_html(source=data)
        return nodes.raw('', html['body'], format='html')

    def _raw_fields(self, data, field_name=''):
        body = nodes.field_body()
        if isinstance(data, list):
            for item in data:
                body.append(self._raw_html_block(data=item))
        else:
            body.append(self._raw_html_block(data=data))

        field = nodes.field()
        field.append(nodes.field_name(text=field_name))
        field.append(body)
        return field

    @staticmethod
    def _literal_block(data, language='yaml', dump_data=True):
        if dump_data:
            literal = nodes.literal_block(
                text=DOCYAML.dump(data)
            )
        else:
            literal = nodes.literal_block(text=data)
        literal['language'] = 'yaml'
        return literal

    @staticmethod
    def _section_block(title, text=None):
        section = nodes.section(
            title,
            nodes.title(text=title),
            ids=[nodes.make_id('-'.join(title))],
        )
        if text:
            section_body = nodes.field_body()
            section_body.append(nodes.paragraph(text=text))
            section.append(section_body)

        return section

    def _yaml_section(self, to_yaml_data, section_title, section_text=None):
        yaml_section = self._section_block(
            title=section_title,
            text=section_text
        )
        yaml_section.append(self._literal_block(data=to_yaml_data))
        return yaml_section

    def _run_role(self, role):
        section = self._section_block(
            title='Role Documentation',
            text='Welcome to the "{}" role documentation.'.format(
                os.path.basename(role)
            )
        )
        defaults_file = os.path.join(role, 'defaults', 'main.yml')
        if os.path.exists(defaults_file):
            with open(defaults_file) as f:
                role_defaults = DOCYAML.load(f.read())
            section.append(
                self._yaml_section(
                    to_yaml_data=role_defaults,
                    section_title='Role Defaults',
                    section_text='This section highlights all of the defaults'
                                 ' and variables set within the "{}"'
                                 ' role.'.format(os.path.basename(role))
                )
            )
        vars_path = os.path.join(role, 'vars')
        if os.path.exists(vars_path):
            for v_file in os.listdir(vars_path):
                vars_file = os.path.join(vars_path, v_file)
                with open(vars_file) as f:
                    vars_values = DOCYAML.load(f.read())
                section.append(
                    self._yaml_section(
                        to_yaml_data=vars_values,
                        section_title='Role Variables: {}'.format(v_file)
                    )
                )

        test_list = nodes.field_list()
        test_section = self._section_block(
            title='Molecule Scenarios',
            text='Molecule is being used to test the "{}" role. The'
                 ' following section highlights the drivers in service'
                 ' and provides an example playbook showing how the role'
                 ' is leveraged.'.format(os.path.basename(role))
        )
        molecule_path = os.path.join(role, 'molecule')
        if os.path.exists(molecule_path):
            for test in os.listdir(molecule_path):
                molecule_section = self._section_block(
                    title='Scenario: {}'.format(test)
                )
                molecule_file = os.path.join(
                    molecule_path,
                    test,
                    'molecule.yml'
                )
                if not os.path.exists(molecule_file):
                    continue

                with open(molecule_file) as f:
                    molecule_conf = DOCYAML.load(f.read())

                driver_data = molecule_conf.get('driver')
                if driver_data:
                    molecule_section.append(
                        nodes.field_name(
                            text='Driver: {}'.format(
                                driver_data['name']
                            )
                        )
                    )

                    options = driver_data.get('options')
                    if options:
                        molecule_section.append(
                            self._yaml_section(
                                to_yaml_data=options,
                                section_title='Molecule Options'
                            )
                        )

                provisioner_data = molecule_conf.get('provisioner')
                if provisioner_data:
                    inventory = provisioner_data.get('inventory')
                    if inventory:
                        molecule_section.append(
                            self._yaml_section(
                                to_yaml_data=inventory,
                                section_title='Molecule Inventory'
                            )
                        )

                molecule_playbook_path = os.path.join(
                    molecule_path,
                    test,
                    'converge.yml'
                )
                if not os.path.exists(molecule_playbook_path):
                    molecule_playbook_path = os.path.join(
                        molecule_path,
                        test,
                        'playbook.yml'
                    )
                with open(molecule_playbook_path) as f:
                    molecule_playbook = DOCYAML.load(f.read())
                molecule_section.append(
                    self._yaml_section(
                        to_yaml_data=molecule_playbook,
                        section_title='Example {} playbook'.format(test)
                    )
                )
                test_list.append(molecule_section)
            else:
                test_section.append(test_list)
                section.append(test_section)

        self.run_returns.append(section)

        # Document any libraries nested within the role
        library_path = os.path.join(role, 'library')
        if os.path.exists(library_path):
            self.options['documentation'] = True
            self.options['examples'] = True
            for lib in os.listdir(library_path):
                if lib.endswith('.py'):
                    self._run_module(
                        module=self.load_module(
                            filename=os.path.join(
                                library_path,
                                lib
                            )
                        ),
                        module_title='Embedded module: {}'.format(lib),
                        example_title='Examples for embedded module'
                    )

    def _run_module(self, module, module_title="Module Documentation",
                    example_title="Example Tasks"):
        if self.options.get('documentation'):
            docs = self.build_documentation(module=module)
            self.run_returns.append(
                self.make_node(
                    title=module_title,
                    contents=docs
                )
            )

        if self.options.get('examples'):
            examples = self.build_examples(module=module)
            self.run_returns.append(
                self.make_node(
                    title=example_title,
                    contents=examples,
                    content_type='yaml'
                )
            )

    def run(self):
        """Run the plugin."""
        self.run_returns = list()

        if self.options.get('module'):
            module_path = os.path.join(os.environ["PROJECT_ROOT"],
                                       self.options['module'])
            module = self.load_module(filename=module_path)
            self._run_module(module=module)

        if self.options.get('role'):
            role = os.path.join(os.environ["PROJECT_ROOT"],
                                self.options['role'])
            self._run_role(role=role)

        return self.run_returns


def setup(app):
    """Configure the plugin."""
    classes = [
        AnsibleAutoPluginDirective,
    ]
    for directive_class in classes:
        app.add_directive(directive_class.directive_name, directive_class)

    return {'version': '0.2'}
