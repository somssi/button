import sys
import argparse
import importlib
import glob
import time

from button.tasks import Task


class EnumerationTask(Task):
    def __init__(self, tasks):
        super().__init__('tasks', 'display the list of tasks')
        self.tasks = tasks

    def add_arguments(self, _parser):
        pass

    def run(self, _parsed):
        names = [task.name for task in self.tasks]
        descs = [task.desc for task in self.tasks]
        maxlen_names = max([len(name) for name in names])

        print('Tasks:')
        for i in range(len(names)):
            print('  {:{width}}  {}'.format(names[i], descs[i], width=maxlen_names))


def main():
    parser = argparse.ArgumentParser(description='button', add_help=False)
    parser.add_argument('--taskdir', type=str, default='.button')
    parser.add_argument('--no-timing', action='store_true')

    # load user-defined tasks from taskdir
    parsed, _ = parser.parse_known_args()
    tasks = []

    filenames = glob.glob('{}/*.py'.format(parsed.taskdir))
    for fn in filenames:
        spec = importlib.util.spec_from_file_location('', fn)
        user_defined = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(user_defined)
        for task_cls in user_defined.tasks:
            tasks.append(task_cls())

    # define default task "tasks": enumerate tasks
    tasks.append(EnumerationTask(tasks))

    # add subparsers
    subparsers = parser.add_subparsers(title='subcommands')
    for task in tasks:
        task_parser = subparsers.add_parser(task.name, description=task.desc)
        task.add_arguments(task_parser)
        task_parser.set_defaults(func=task.run)

    parsed = parser.parse_args()
    if hasattr(parsed, 'func'):
        time_started = time.time()
        parsed.func(parsed)
        if not parsed.no_timing:
            print('[Task completed in {:.4f} secs]'.format(time.time() - time_started))