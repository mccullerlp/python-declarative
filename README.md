# Declarative Python

Collection of decorators and base classes to allow a declarative style of programming. The 
underlying philosophy can be described as "init considered harmful". Instead, object attributes
are constructed from decorator functions and then stored. This is essentially like the @property
decorator, but @declarative.mproperty additionally _stores_ (memoizes) the result. Unlike the @property
builtin, @declarative.mproperty can take an argument, providing convenient parameterization and transformation
of inputs.

For classes inheriting declarative.OverridableObject, the @declarative.dproperty attribute can be used
and all properties will be called/accessed within the __init__ constructor to ensure construction. This allows
objects to register with other objects and is convenient for event-loop reactor programming.

The Argparse sub-library allows the user to create quick command-line interfaces to create and run methods in declarative fashion.

The technique of access->construction means that the dependencies between class attributes are resolved
automatically. During the construction of each attribute, any required attributes are accessed and therefore
constructed if they haven't already been.

The price for the convenience is that construction becomes implicit and recursive. The wrappers in this library
do some error checking to aid with this and to properly report AttributeError. Code also ends up somewhat more
verbose with the decorator boilerplate.

## Quick Example

```python
import declarative

class Child(object):
    id = None

class Parent(object):
    @declarative.mproperty
    def child_registry(self):
        return set()

    @declarative.mproperty
    def c1(self):
        print("made Parent.c1")
        child = Child()
        child.id = 1
        self.child_registry.add(child)
        return child

    @declarative.mproperty
    def c2(self):
        print("made Parent.c2")
        child = Child()
        child.id = 2
        self.child_registry.add(child)
        return child

parent = Parent()
parent.c1
#>> made Parent.c1
parent.c2
#>> made Parent.c2
print(parent.child_registry)
```

Ok, so now as the child object attributes are accessed, they are also registered.

## More automatic Example

```python
import declarative

class Child(declarative.OverridableObject):
    id = None

class Parent(declarative.OverridableObject):
    @declarative.mproperty
    def child_registry(self):
        return set()

    @declarative.dproperty
    def c1(self, val = None):
        if val is None:
            child = Child(
                id = 1,
            )
            print("made Parent.c1")
        else:
            print("Using outside c1")
            child = val
      
        self.child_registry.add(child)
        return child

    @declarative.dproperty
    def c2(self):
        child = Child(
            id = 2,
        )
        print("made Parent.c2")
        self.child_registry.add(child)
        return child

    @declarative.dproperty
    def c2b(self):
        child = Child(
            id = self.c2.id + 0.5
        )
        print("made Parent.c2b")
        self.child_registry.add(child)
        return child

parent = Parent()
#>> made Parent.c2
#>> made Parent.c2b
#>> made Parent.c1
print(parent.child_registry)
```

Now the registry is filled instantly.

Alternatively, c1 for this object can be replaced.


```
parent = Parent(
    c1 = Child(id = 8)
)
#>> made Parent.c2
#>> made Parent.c2b
#>> using outside c1
print(parent.child_registry)
```

No __init__ function! 

## Numerical Usage

This technique can be applied for memoized numerical results, particularly when you might 
want to canonicalize the inputs to use a numpy representation.

```python
import declarative

class MultiFunction(declarative.OverridableObject):
    @declarative.dproperty
    def input_A(self, val):
        #not providing a default makes them required keyword arguments
        #during construction
        return numpy.asarray(val)

    @declarative.dproperty
    def input_B(self, val):
        return numpy.asarray(val)

    @declarative.mproperty
    def output_A(self):
        #note usage of mproperty. This will only be computed if accessed, not at construction
        return self.input_A + self.input_B

    @declarative.mproperty
    def output_B(self):
        #note the use of incremental computing into output_A
        return self.input_A * self.input_B - self.output_A

data = MultiFunction(
    input_A = [1,2,3],
    input_B = [4,5,6],
)
print(data.output_A)
```

## Additional Features

### Argparse interface
Mentioned above. Some additional annotations and run methods can allow objects to be called and accessed from the command line, without a special interface while providing improved composition of declarative programming.

### Bunches
These are dictionary objects that also allow indexing through the '.' attribute access operator. Other libraries provide these, but the ones included here are

* Bunch - just a dictionary wrapper. It also wraps any dictionary's that are stored to provide a consistent interface.
* DeepBunch - Allows nested access without construction of intermediate dictionary's. Extremely convenient for configuration management of hierarchical systems.
* HDFDeepBunch - DeepBunch adapted so that the underlying storage are HDF5 data groups using the h5py library. Automatically converts to/from numpy arrays and unwraps values. DeepBunch's containing compatible numbers/arrays can be directly embedded into hdf. This allows configuration storage with datasets.

See the Bunch page for more.

### Relays and Callbacks
A number of objects are provided for reactor programming. These are RelayValue and RelayBool which store values and run callbacks upon their change. This is similar Qt's signal/socket programming but lightweight for python.

### Substrate System
This is the culmination of the declarative techniques to hierarchical simulation and modeling. Child objects automatically embed into parent objects and gain access to nonlocal data and registration interfaces. It invokes considerably more "magic" than this library typically need. Currently used by the python physics/controls simulation software openLoop.

## Development
This library was developed in initial form to generate the Control System and interfaces of the Holometer experiment at Fermilab. The underlying technology for that is the EPICS distributed experimental control library (developed at Argonne). 

RelayBool and RelayValue objects were bound to EPICS variables using the declarative construction methods of this library. Further logic cross-linked variables and interfaced to hardware. Bunches were used for configuration management. HDFDeepBunch was used for data analysis.


## Related Documentation
Using multiple inheritance and mixins becomes very simple with this style of programming, but super is often needed, but forces the use of keyword arguments. Since this library forces them anyway, this site details other considerations for using super:
 *  https://fuhm.net/super-harmful/
 
 
