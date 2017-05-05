# Python-Declarative

For full documentation visit [python-declarative](https://github.org).

Checkout [[README]]

## Commands

* `mkdocs new [dir-name]` - Create a new project.
* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.
* `mkdocs help` - Print this help message.

## Project layout

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

parent = Parent()
parent.c1
#>> Making Parent.c1
parent.c2
#>> Making Parent.c2
print parent.child_registry
```

