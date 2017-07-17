# habitica-planner
[![PyPI](https://img.shields.io/pypi/v/habitica_planner.svg)](https://pypi.python.org/pypi/habitica_planner)  [![PyPI](https://img.shields.io/pypi/l/habitica_planner.svg)](https://pypi.python.org/pypi/habitica_planner)

Simple Python script to upload multiple tasks to Habitica.
Uses awesome [`habitica` python api](https://github.com/philadams/habitica) and PyYAML.

## Usage
```
habitica_planner some-file.yml > some-file.out.yml
```
`some-file.yml` is the input of the scipt. An example:
```
- 'Quest :one:':
    - priority: 2.0
    - 'Go east :arrow_right:': 1.5
    - 'Go west :arrow_left:': 1.0
    - Breakfast:
        - priority: 2.0
        - Make fire: 2.0
        - Boil water
        - Cook gruel: 1.5
        - Eat gruel
    - Sleep : 0.5
- 'Quest :two:':
    - 'Finish Quest :one: ![progress](http://progressed.io/bar/98)'
```
If a task has any Markdown syntax, it should be put inside `''`. A task can be either a single task or a checklist tasks. For example of a single task see `Make fire` and `Boil water` tasks, and for checklist task are `Quest :one:`, `Breakfast` and `Quest :two:`.

__AN IMPORTANT NOTE__: Do __NOT__ put tasks with names `priority`, `id` and `checklist_id`, those are technical keys of `habitica_planner`.
