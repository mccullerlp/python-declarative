# -*- coding: utf-8 -*-
"""
TODO, needs big documentation
"""
from __future__ import (
    division,
    print_function,
    absolute_import,
)

import sys
import argparse
import collections

from ..bunch import Bunch
from ..overridable_object import OverridableObject
from ..utilities import SuperBase, NOARG
from ..properties import mproperty


types = Bunch(
    command  = 'command',
    group    = 'group',
    argument = 'argument',
)


class OOArgParse(
        OverridableObject,
        SuperBase,
        object,
):
    @classmethod
    def __cls_argparse__(
            cls,
            args = None,
            __sys_exit = True,
            __usage_prog__ = None,
            base_kwargs = dict(),
            no_commands = False,
            **exkwargs
    ):
        arguments = dict()
        commands  = dict()
        groups    = dict()
        for attr_name in dir(cls):
            attr_obj = getattr(cls, attr_name)
            arganno = getattr(attr_obj, '_argparse', None)
            if arganno:
                if arganno.type == types.argument:
                    #mask the argument if it was specified in an extra kwarg
                    if attr_name not in exkwargs:
                        arguments[attr_name] = arganno
                elif arganno.type == types.group:
                    groups[attr_name] = arganno
                elif arganno.type == types.command:
                    commands[attr_name] = arganno

        description = getattr(cls, "__arg_desc__", cls.__doc__)

        ap = argparse.ArgumentParser(
            prog        = __usage_prog__,
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
        glist = collections.deque(sorted([(v.order, k, v) for k, v in groups.items()]))
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
        for name, cbunch in commands.items():
            commands_byname[cbunch.cmd_name] = cbunch

        cmdlist = list(k for o, k in sorted((v.order, k) for k, v in commands_byname.items()))

        if not no_commands:
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
        for order, argname, argbunch in sorted([(v.order, k, v) for k, v in arguments.items()]):
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
            spp = ap.add_subparsers(dest = 'command', help = "(May have subarguments, use -h after them for command specific help)")

            if default_cmd is not None:
                if default_cmd.__doc__ is not None:
                    doc = default_cmd.__doc__ + " [Default, no arguments]"
                else:
                    doc = "Default Action [command only]"
                spp.add_parser(
                    '""',
                    help = doc,
                )

            if not no_commands:
                for name, cbunch in commands.items():
                    commands_byname[cbunch.cmd_name] = cbunch
                    if cbunch.takes_arguments:
                        extra = " [takes arguments]"
                    else:
                        extra = " [command only]"
                    spp.add_parser(
                        cbunch.cmd_name,
                        help = cbunch.description + extra,
                    )
            ap.print_help()
            sys.exit(0)

        kwargs = dict(base_kwargs)
        for argname, argbunch in arguments.items():
            val = getattr(args_parsed, argname)
            if val is not NOARG:
                kwargs[argbunch.name_inject] = val

        if commands_byname and not no_commands:
            command = getattr(args_parsed, '__command__', NOARG)
            if command is not None:
                command_idx_in_args = args.index(command)
                call_args = args[:command_idx_in_args]
            else:
                call_args = args[:]
        else:
            command = None
            call_args = args
        args_sub    = getattr(args_parsed, '__args__', NOARG)

        #add in the extra kwargs that were given
        kwargs.update(exkwargs)
        kwargs['__cls_argparse_args__'] = tuple(call_args)
        kwargs['__cls_argparse_cmd__']  = command
        kwargs['__cls_argparse_cmd_args__']  = tuple(args_sub) if args_sub is not NOARG else None
        obj = cls(**kwargs)
        if no_commands:
            return obj

        if command is None:
            ret = obj.__arg_default__()
        else:
            cbunch = commands_byname[command]
            call = getattr(obj, cbunch.run_name)
            #TODO, check about taking additional arguments
            if not cbunch.takes_arguments and args_sub:
                raise RuntimeError("Final Command does not take additional arguments")
            ret = call(args_sub)
        if __sys_exit:
            sys.exit(ret)
        return ret

    @mproperty
    def __cls_argparse_args__(self, args = None):
        return args

    @mproperty
    def __cls_argparse_cmd__(self, args = None):
        return args

    @mproperty
    def __cls_argparse_cmd_args__(self, args = None):
        return args
