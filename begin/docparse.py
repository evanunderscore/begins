from collections import defaultdict, namedtuple
import inspect
import logging
from xml.etree import ElementTree

from docutils.core import publish_doctree

try:
    from inspect import signature
except ImportError:
    from funcsigs import signature

# Ordering is important here; we don't want to accidentally get future's
# builtins module on 2.x!
try:
    import __builtin__ as builtins
except ImportError:
    import builtins

logging.basicConfig()
log = logging.getLogger(__name__)


Doc = namedtuple('Doc', ('text', 'params'))
Param = namedtuple('Param', ('text', 'type'))


def parse_doc(func):
    doc = inspect.getdoc(func)
    if doc is None:
        return Doc(None, None)

    dom = publish_doctree(doc).asdom()
    etree = ElementTree.fromstring(dom.toxml())

    doctext = '\n\n'.join(x.text for x in etree.findall('paragraph'))

    fields = []
    for field_list in etree.findall('field_list'):
        fields += [x for x in field_list.findall('field')]

    params = defaultdict(dict)
    for field in fields:
        field_name = field.find('field_name')
        field_body = field.find('field_body')
        parts = field_name.text.split()
        if len(parts) < 2:
            log.debug('ignoring field %s', field_name.text)
            continue
        doctype, name = parts
        text = ''.join(field_body.itertext())
        log.debug('%s %s: %s', doctype, name, text)
        params[name][doctype] = text

    tuples = {}
    for name, values in params.items():
        tuples[name] = Param(values.get('param'), values.get('type'))
    return Doc(doctext, tuples)


def evaluate(name, stack_depth=None):
    """Find an object by name.

    :param name: Name of the object to evaluate. May contain dotted lookups,
        e.g. 'a.b' finds 'a' in the target frame, then looks inside 'a'
        to find 'b'.
    :type name: str
    :param stack_depth: How far up the stack to evaluate locals and globals.
        Specify 0 for your frame, 1 for your caller's frame, etc.
        If unspecified, `name` is assumed to refer to a builtin.
    :type stack_depth: int
    """
    log.debug('evaluating %s', name)
    things = dict(vars(builtins))
    if stack_depth is not None:
        things.update(inspect.stack()[stack_depth + 1][0].f_locals)
        things.update(inspect.stack()[stack_depth + 1][0].f_globals)
    parts = name.split('.')
    thing = things[parts[0]]
    for part in parts[1:]:
        things = vars(thing)
        thing = things[part]
    log.debug('evaluated to %r', thing)
    return thing
