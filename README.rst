Declarative Python
==================

Collection of decorators and base classes to allow a declarative style
of programming. The underlying philosophy is "init considered harmful".

Quick Example
=============

import declarative

class Child(object): id = None

class Parent(object): @declarative.mproperty def child\_registry(self):
return set()

::

    @declarative.mproperty
    def c1(self):
        print "Making Parent.c1"
        child = Child()
        child.id = 1
        self.child_registry.add(child)
        return child

    @declarative.mproperty
    def c2(self):
        print "Making Parent.c2"
        child = Child()
        child.id = 1
        self.child_registry.add(child)
        return child

parent = Parent() parent.c1 >> Making Parent.c1 parent.c2 >> Making
Parent.c2 print parent.child\_registry

Ok, so now as the

More automatic Example
======================

Documentation
=============

TODO Provide Link

Related Documentation
=====================

-  https://fuhm.net/super-harmful/
