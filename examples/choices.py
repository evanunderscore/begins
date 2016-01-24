"""Example showing choices in begins.

Choices require the Enum class introduced in Python 3.4.
For earlier versions, you can install the backport with "pip install enum34".

Code usage:
    automatic()
    explicit(Choices.bar)
    automatic(arg=Choices.baz)

Command line usage:
    choices.py automatic
    choices.py explicit bar
    choices.py automatic --arg baz
    choices.py explicit bad  # exception displays possible choices
"""
from enum import Enum

import begin
from begin.utils import toenum


class Choices(Enum):
    foo = 1
    bar = 2.0
    baz = '03'


@begin.subcommand
@begin.convert(arg=toenum(Choices))
def explicit(arg):
    print('you chose Choices.{} -> {}'.format(arg.name, arg.value))


@begin.subcommand
@begin.convert(_automatic=True)
def automatic(arg=Choices.foo):
    print('you chose Choices.{} -> {}'.format(arg.name, arg.value))


@begin.start
def main():
    pass
