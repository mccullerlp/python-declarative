"""
TODO, needs big documentation
"""
from __future__ import (
    division,
    print_function,
    absolute_import,
)
import argparse
import collections

from .. import (
    Bunch,
    NOARG
)


import sys
from ..overridable_object import OverridableObject
from ..utilities.representations import SuperBase


types = Bunch(
    command  = 'command',
    group    = 'group',
    argument = 'argument',
)


class OOArgParse(OverridableObject, SuperBase, object):
    @classmethod
    def __cls_argparse__(cls, args = None):
        arguments = dict()
        commands  = dict()
        groups    = dict()
        for attr_name in dir(cls):
            attr_obj = getattr(cls, attr_name)
            arganno = getattr(attr_obj, '_argparse', None)
            if arganno:
                if arganno.type == types.argument:
                    arguments[attr_name] = arganno
                elif arganno.type == types.group:
                    groups[attr_name] = arganno
                elif arganno.type == types.command:
                    commands[attr_name] = arganno

        description = getattr(cls, "__arg_desc__", cls.__doc__)

        ap = argparse.ArgumentParser(
            description = description,
            add_help    = False
        )
        ap.add_argument(
            '-h', '--help', '--halp!',
            dest = 'help',
            action='store_true',
            help = "Show this help screen"
            #help = argparse.SUPPRESS,
        )

        #build groups
        glist = collections.deque(sorted([(v.order, k, v) for k, v in groups.iteritems()]))
        gengroups = dict()
        gengroups[None] = ap

        while glist:
            order, name, gbunch = glist.pop()
            useparse = gengroups.get(gbunch.group, None)
            if useparse is None:
                if gbunch.group not in groups:
                    raise RuntimeError("Group {0} not defined!".format(gbunch.group))
                #reinsert in back
                glist.appendleft((name, gbunch))
                continue
            group = gbunch.func(useparse)
            gengroups[name] = group

        default_cmd = getattr(cls, "__arg_default__", None)
        commands_byname = dict()
        for name, cbunch in commands.iteritems():
            commands_byname[cbunch.cmd_name] = cbunch

        cmdlist = list(k for o, k in sorted((v.order, k) for k, v in commands_byname.iteritems()))

        if default_cmd is None:
            ap.add_argument(
                '__command__',
                metavar = 'COMMAND',
                choices = cmdlist,
                help = argparse.SUPPRESS,
            )
        else:
            if commands_byname:
                ap.add_argument(
                    '__command__',
                    metavar = 'COMMAND',
                    choices = cmdlist + [""],
                    default = None,
                    nargs='?',
                    help = argparse.SUPPRESS,
                )

        if len(commands_byname) > 0:
            ap.add_argument(
                '__args__',
                metavar = 'args',
                nargs=argparse.REMAINDER,
                help = argparse.SUPPRESS,
            )

        argdo = dict()
        for order, argname, argbunch in sorted([(v.order, k, v) for k, v in arguments.iteritems()]):
            useparse = gengroups.get(argbunch.group, None)
            argdo[argname] = argbunch.func(useparse)

        if args is None:
            args = sys.argv[1:]

        print_help = False
        #TODO fix -h handling requiring otherwise perfect other arguments
        if '-h' in args or '--help' in args or '--halp!' in args:
            try:
                class BooBoo(Exception):
                    pass
                def error(message):
                    raise BooBoo(message)
                ap.error = error
                args_parsed = ap.parse_args(args)
                print_help = args_parsed.help
            except BooBoo:
                print_help = True
        else:
            args_parsed = ap.parse_args(args)
            print_help = args_parsed.help

        if print_help:
            spp = ap.add_subparsers(dest = 'command', help = "(May have subarguments, use -h after them)")

            if default_cmd is not None:
                if default_cmd.__doc__ is not None:
                    doc = default_cmd.__doc__ + " [Default]"
                else:
                    doc = "Default Action"
                spp.add_parser(
                    '[""]',
                    help = doc,
                )

            for name, cbunch in commands.iteritems():
                commands_byname[cbunch.cmd_name] = cbunch
                spp.add_parser(
                    cbunch.cmd_name,
                    help = cbunch.description,
                )
            ap.print_help()
            sys.exit(0)

        kwargs = dict()
        for argname, argbunch in arguments.iteritems():
            val = getattr(args_parsed, argname)
            if val is not NOARG:
                kwargs[argbunch.name_inject] = val

        if commands_byname:
            command = getattr(args_parsed, '__command__', NOARG)
        else:
            command = None
        args    = getattr(args_parsed, '__args__', NOARG)

        obj = cls(**kwargs)

        if command is None:
            ret = obj.__arg_default__()
        else:
            cbunch = commands_byname[command]
            call = getattr(obj, cbunch.run_name)
            ret = call(args)
        return ret

