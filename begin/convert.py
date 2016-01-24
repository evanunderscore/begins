"Type casting for function arguments"
from __future__ import absolute_import, division, print_function
import functools
import sys

try:
    from inspect import signature
except ImportError:
    from funcsigs import signature

from begin import utils
from begin import docparse

__all__ = ['convert']


CONVERTERS = {
        str: lambda _: str,
        int: lambda _: int,
        float: lambda _: float,
        bool: lambda _: utils.tobool,
        tuple: lambda _: utils.tolist,
        list: lambda _: utils.tolist,
        type(sys.stdin): lambda src: functools.partial(utils.tofile, mode=src.mode),
}

if sys.version_info[0] < 3:
    CONVERTERS[long] = lambda _: long


def convert(_automatic=False, **mappings):
    """Cast function arguments to decorated function.

    Optionally use callables to cast the arguments for the decorated functions.

    >>> import begin
    >>> @begin.convert(second=int)
    ... def func(first, second=None):
    ...     pass

    If a value is passed as the 'second' argument to 'func', it will be
    replaced with the result of calling the 'int' function with the value. If
    no value is passed, the default value will be used without casting.

    Casting also works for variable position arguments. In this case the
    casting function is called on each argument.

    >>> @begin.convert(args=float)
    ... def func(*args):
    ...    pass

    Helper functions for casting arguments can be found in the 'begin.utils'
    module.
    """
    def decorator(func):
        target = func
        while hasattr(target, '__wrapped__'):
            target = getattr(target, '__wrapped__')
        sig = signature(target)
        if _automatic:
            for param in sig.parameters.values():
                if param.name in mappings or param.default is param.empty:
                    continue
                converter = CONVERTERS.get(type(param.default))
                if converter:
                    mappings[param.name] = converter(param.default)
        return _get_wrapper(func, sig, mappings)
    return decorator


def doctyped(func=None, **converter_overrides):
    """Alternative to convert which parses types from a docstring.

    >>> @doctyped
    ... def func():
    ...    pass

    If expecting an instance of a custom class which has a method `fromstring`,
    it will be used as the conversion function.

    >>> class IntList(list):
    ...     @classmethod
    ...     def fromstring(cls, string):
    ...         return cls(int(x) for x in string.split(','))

    If the docstring references types begins cannot parse, you can supply
    parsers as keyword arguments and this acts as a decorator factory.
    In this example, `parse_foo` takes a string and returns a `Foo` instance.

    >>> @doctyped(Foo=parse_foo)
    ... def func(foo):
    ...     pass

    Converters for qualified names cannot be passed directly and must instead
    be passed in an unpacked dict.

    >>> @doctyped(**{'foo.Bar': parse_foobar})
    ... def func(bar):
    ...     pass
    """
    def decorator(func):
        mappings = {}
        converters = dict(CONVERTERS)
        for name, converter in converter_overrides.items():
            type_ = docparse.evaluate(name, stack_depth=depth)
            converters[type_] = _make_converter(converter)
        target = func
        while hasattr(target, '__wrapped__'):
            target = getattr(target, '__wrapped__')
        sig = signature(target)
        doc = docparse.parse_doc(func)
        for param in sig.parameters.values():
            if param.name not in doc.params:
                msg = 'could not find docstring entry for {}'.format(param.name)
                raise ValueError(msg)
        for name, param in doc.params.items():
            if param.type is None:
                msg = 'could not find type in docstring entry for {}'.format(name)
                raise ValueError(msg)
            param_type = docparse.evaluate(param.type, stack_depth=depth)
            if hasattr(func, '__annotations__'):
                func.__annotations__[name] = '{} [{}]'.format(param.text, param.type)
            converter = converters.get(param_type)
            if converter:
                mappings[name] = converter(None)
            elif hasattr(param_type, 'fromstring'):
                mappings[name] = param_type.fromstring
            else:
                raise Exception('no known converter for {}'.format(param_type))
        return _get_wrapper(func, sig, mappings)
    if func is not None:
        depth = 2
        return decorator(func)
    depth = 1
    return decorator


def _get_wrapper(func, sig, mappings):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args = list(args)
        for pos, param in enumerate(sig.parameters.values()):
            if param.name not in mappings:
                continue
            if param.kind == param.POSITIONAL_ONLY:
                args[pos] = _convert(mappings, param, args[pos])
            if param.kind == param.POSITIONAL_OR_KEYWORD:
                if param.name in kwargs and \
                        kwargs[param.name] is not param.default:
                    kwargs[param.name] = _convert(mappings, param,
                                                  kwargs[param.name])
                elif pos < len(args) and \
                        args[pos] is not param.default:
                    args[pos] = _convert(mappings, param, args[pos])
            if param.kind == param.KEYWORD_ONLY and \
                    kwargs[param.name] is not param.default:
                kwargs[param.name] = _convert(mappings, param,
                                              kwargs[param.name])
            if param.kind == param.VAR_POSITIONAL:
                start = pos
                for pos in range(start, len(args)):
                    args[pos] = _convert(mappings, param, args[pos])
            if param.kind == param.VAR_KEYWORD:
                msg = 'Variable length keyword arguments not supported'
                raise ValueError(msg)
        return func(*args, **kwargs)
    # do not skipping decorators when unwinding wrapping
    wrapper.__wrapped__ = func
    return wrapper


def _make_converter(func):
    return lambda _: func


def _convert(mappings, param, value):
    if isinstance(value, str):
        value = mappings[param.name](value)
    return value
