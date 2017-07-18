"""
    habitica_planner -- plan multiple recusive tasks with checklists
    Copyright 2017 Pavel Pletenev <cpp.create@gmail.com>
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
# pylint: disable=invalid-name
import os
import sys
import gettext
import tempfile
from typing import Union, List
import pkg_resources
import yaml
from habitica.core import AUTH_CONF, load_auth
import habitica.api as hapi
from plumbum.cli import Application, Predicate
from plumbum.cli.terminal import Progress
from plumbum import local, FG


def install(package_name='habitica_planner'):
    'finds and installs translation for package'
    # pylint: disable=undefined-loop-variable
    for localedir in pkg_resources.resource_filename(package_name, 'i18n'), None:
        localefile = gettext.find(package_name, localedir)
        if localefile:
            break
    gettext.install(package_name, localedir, names=('ngettext',))
    return _


_ = install()


class Task:
    'self-descriptive'
    def __init__(self, name: str = None, data: Union[List, int, float] = 1.0) -> None:
        self.name = name
        self.checklist = []  # type: List[Task]
        self.priority = 1.0
        self.id = None  # type: Union[None, str]
        self.checklist_id = None  # type: Union[None, str]
        if not isinstance(data, list):
            self.priority = data
            data = []
        for e in data:
            if isinstance(e, str):
                self.checklist.append(Task(e))
                continue
            if isinstance(e, dict):
                if len(e) != 1:
                    raise ValueError(
                        'Strange dict from YAML parser: {}'.format(e))
                k = tuple(e.keys())[0]
                if k == 'priority':
                    if e[k] in [0.5, 1, 1.5, 2]:
                        self.priority = e[k]
                    else:
                        raise ValueError(
                            'Invalid priority for task {}.\
                            Expected one of 0.5, 1, 1.5, 2. Got: {}'.format(self.name, e[k]))
                    continue
                if k in ['id', 'checklist_id']:
                    setattr(self, k, e[k])
                if isinstance(e[k], (list, int, float)):
                    self.checklist.append(Task(k, e[k]))
                    continue
                raise ValueError(
                    'Unexpected element type {} of element {}'.format(type(e), e))

    def __repr__(self):
        message = '<Task {self.name} priority {self.priority} with subtasks {self.checklist}>'
        return message.format(self=self)

    def pretty_string(self, ind=0):
        'show markdown-like list of tasks'
        res = '    ' * ind + '{}{}'
        name = '' if self.name is None else '- ' + self.name
        priority = '' if self.name is None else '({})'.format(self.priority)
        ind += 0 if self.name is None else 1
        res = res.format(name, priority)
        cl = '\n'.join(map(lambda x: x.pretty_string(ind), self.checklist))
        res += ('\n' if self.name else '') + cl if cl else ''
        return res

    def will_be_pushed(self):
        'output individual tasks'
        res = ''
        if self.name:
            res += _("Task {self.name} with priority {self.priority}\n").format(  # noqa: Q000
                self=self)
            for task in self.checklist:
                res += _("    - {}\n").format(task.name)  # noqa: Q000
        for task in self.checklist:
            res += task.will_be_pushed()
        return res

    def push(self, api):
        'send data to habitica server'
        if self.name:
            resp = api.user.tasks(
                type='todo', text=self.name,
                priority=str(self.priority), _method='post')
            self.id = resp['id']
            task_number = 0
            for task in self.checklist:
                if task.name:
                    task_number += 0
                    resp = api.tasks.checklist(
                        _uri_template='{0}/{self.resource}/{aspect_id}/{self.aspect}',
                        _id=self.id, text=task.name, _method='post')
                    task.checklist_id = resp['checklist'][task_number]['id']
        for task in Progress(self.checklist):
            task.push(api)

    def __iter__(self):
        if self.name:
            for prop in ['id', 'checklist_id', 'priority']:
                val = getattr(self, prop)
                if val:
                    yield {prop: val}
        for task in self.checklist:
            if task.name:
                yield {task.name: list(task)}


def swap_out_err():
    'swap stdout and stderr'
    err = sys.stderr
    sys.stderr = sys.stdout
    sys.stdout = err


@Predicate
def OptionalFile(f):
    'predicate like ExistingFile'
    f = local.path(f)
    if f.exists() and f.is_file():
        return f


EXAMPLE_TASK_FILE = _("""
#Write your tasks here, save and exit
#Example:
#- An example task
#    - An example subtask
#    - Second example subtask with priority:2.0
""")


class HabiticaPlanner(Application):
    # pylint: disable=arguments-differ,missing-docstring
    __doc__ = _("habitica_planner -- plan multiple recusive tasks with checklists")  # noqa: Q000

    def main(self, file: OptionalFile = None):
        'main algorithm'
        hab = hapi.Habitica(load_auth(AUTH_CONF))
        if file is None:
            editor = local[os.environ.get('EDITOR', 'nano')]
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                f.write(EXAMPLE_TASK_FILE)
                f.file.close()
                editor[f.name] & FG()  # pylint: disable=expression-not-assigned
                with open(f.name) as newf:
                    content = newf.read()
                local['rm'](f.name)
        else:
            with open(file) as f:
                content = f.read()
        swap_out_err()
        d = yaml.load(content)
        if not d:
            print(_("Tasks not found. Exiting."))  # noqa: Q000
            return 1
        t = Task(data=d)
        print(_("Found this this tasks"))  # noqa: Q000
        print(t.will_be_pushed(), end='')
        r = input(_("Push to Habitica?[Y/n]"))  # noqa: Q000
        if r in ['n', _("n")]:  # noqa: Q000
            return 1
        t.push(hab)
        d = list(t)  # type: ignore # because python/mypy#2220
        swap_out_err()
        print(yaml.dump(d, encoding='utf-8', allow_unicode=True).decode('utf-8'))


def main():
    'main for console_scripts'
    HabiticaPlanner().run()


if __name__ == '__main__':
    main()
