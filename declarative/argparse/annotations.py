# -*- coding: utf-8 -*-
"""
"""
from __future__ import (
    division,
    print_function,
    absolute_import,
)

from .. import (
    Bunch,
    NOARG
)

from .oo_argparse import types


def store_true(*args, **kwargs):
    return argument(
        *args,
        action = 'store_true',
        metavar = NOARG,
        **kwargs
    )

def store_false(*args, **kwargs):
    return argument(
        *args,
        action = 'store_false',
        metavar = NOARG,
        **kwargs
    )

def argument(
        calls       = None,
        func        = None,
        name        = None,
        metavar     = None,
        default     = NOARG,
        description = None,
        order       = None,
        group       = None,
        **kwargs
):
    def annotate_argument(func):
        if name is None:
            _name = func.__name__
        else:
            _name = name
        if metavar is None:
            _metavar = func.__name__,
        else:
            _metavar = metavar
        if description is None:
            _description = func.__doc__
        else:
            _description = description
        if not calls:
            _calls = ['--' + _name]
        else:
            _calls = calls
        if callable(default):
            _default = default()
        else:
            _default = default
        if _default is not NOARG:
            _description = _description.replace('{default}', str(_default))
        def gen_argument(parser):
            kw = dict(kwargs)
            kw.update(
                #name    = _name,
                default = _default,
                help = _description,
                dest = func.__name__,
            )
            if _metavar is not NOARG:
                kw['metavar'] = _metavar
            g = parser.add_argument(*_calls, **kw)
            return g
        func._argparse = Bunch(
            type        = types.argument,
            name        = _name,
            name_inject = func.__name__,
            func        = gen_argument,
            group       = group,
            order       = order,
        )
        return func
    if func is None:
        return annotate_argument
    else:
        return annotate_argument(func)

#def arg_bool(func, ):
    #return

def group(
        func = None,
        name = None,
        description = None,
        #group = None,
        mutually_exclusive = False,
        order = None,
        **kwargs
):
    group = None
    def annotate_group(func):
        if not descriptor_check(func):
            raise RuntimeError("Must be a memoized descriptor")
        if name is None:
            _name = func.__name__
        else:
            _name = name
        if mutually_exclusive:
            _name = _name + " [Mutually Exclusive]"
        if description is None:
            _description = func.__doc__
        else:
            _description = description
        def gen_group(parser):
            g = parser.add_argument_group(
                _name,
                description = _description,
                **kwargs
            )
            if mutually_exclusive:
                g = g.add_mutually_exclusive_group()
            return g
        func._argparse = Bunch(
            type  = types.group,
            name  = _name,
            func  = gen_group,
            group = group,
            order       = order,
        )
        return func
    if func is None:
        return annotate_group
    else:
        return annotate_group(func)

def command(
        func            = None,
        name            = None,
        description     = None,
        order           = None,
        takes_arguments = False,
        **kwargs
):
    def annotate_command(func):
        if name is None:
            _name = func.__name__
        else:
            _name = name
        if description is None:
            _description = func.__doc__
        else:
            _description = description
        func._argparse = Bunch(
            type            = types.command,
            cmd_name        = _name,
            description     = _description,
            run_name        = func.__name__,
            order           = order,
            takes_arguments = takes_arguments,
        )
        return func
    if func is None:
        return annotate_command
    else:
        return annotate_command(func)


def descriptor_check(obj):
    #TODO rubustify
    if not isinstance(obj, object):
        raise RuntimeError("Argparse decorator must be outermost decorator")
        return False
    return True





