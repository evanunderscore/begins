"""Example showing command lines from docstrings.

Types read from the docstring are evaluated in the local namespace.

If you have a version of Python that supports function annotations,
you will see help information filled in for the parameters.

Code usage:
    s = Secret()
    s.secret = '@doctyped is great!'
    main('Hi there!',
         Animal('cow', 4),
         date=datetime.datetime(2015, 9, 13),
         secret=s)

Command line usage:
    docs.py "Hi there!" cow.4 --date 2015-09-13 --secret "@doctyped is great!"
"""
import datetime

import begin


def parse_time(string):
    """Parse a datetime from a string using a simple fixed format."""
    return datetime.datetime.strptime(string, '%Y-%m-%d')


class Animal(object):
    """An animal with a name and some legs."""
    def __init__(self, name, legs):
        self.name = name
        self.legs = legs

    def __str__(self):
        return '<<{} with {} legs>>'.format(self.name, self.legs)

    @classmethod
    def fromstring(cls, string):
        """begins uses this to create an Animal from a string."""
        name, legs = string.rsplit('.', 1)
        return cls(name, int(legs))


class Secret(object):
    """Pretend this class came from somewhere else.

    It doesn't give us a nice conversion function.
    """
    def __init__(self):
        self.secret = None

    def __str__(self):
        return ''.join(x if x == ' ' else '*' for x in self.secret)


def parse_secret(string):
    """Convert a string to a Secret."""
    s = Secret()
    s.secret = string
    return s


@begin.start
@begin.doctyped(Secret=parse_secret, **{'datetime.datetime': parse_time})
def main(greeting, animal, date=None, secret=None):
    """Say hello and give me an animal.

    You can also give me a date and tell me a secret if you like.

    :param greeting: A friendly greeting message.
        This one is a builtin type; I can parse this on my own.
    :type greeting: str

    :param animal: An animal with any number of legs.
        I see Animal has a fromstring method; I know how to use that.
    :type animal: Animal

    :param date: The date you would like me to print.
        You told me to use parse_time to make a datetime.datetime.
    :type date: datetime.datetime

    :param secret: Your deepest, darkest secret.
        You told me to use parse_secret to make a Secret.
    :type secret: Secret
    """
    print('Greetings! {}'.format(greeting))
    print('Here is your animal: {}'.format(animal))
    print('It seems to be growing another leg!')
    animal.legs += 1
    print('Now it looks slightly different: {}'.format(animal))
    if date is not None:
        print('Oh, and the date you gave me: {}'.format(date))
    if secret is not None:
        print('Your secret is safe with me: {}'.format(secret))
