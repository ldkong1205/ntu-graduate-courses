#
# $Id: baseobjects.py 620 2010-01-25 13:54:15Z hat $
#
"""
Generic base classes.

Copy of the Chinetics chinetics.core.baseobjects file.

 - L{BaseObject}: Like C{object} but without the default compare and hashing
                  methods.

 - L{EqualityObject}: A L{BaseObject} but with hooks for easily adding logical
                      equivalence notion to the class.

 - L{ReadOnlyObject}: A L{BaseObject} without allowing assignment of object
                      members.

 - L{EqualityReadOnlyObject}: Combination of L{EqualityObject} and
                              L{ReadOnlyObject}.
"""

class BaseObject(object):
    """
    Generic base class without default compare and hashing functions.
    """
    def __cmp__(self, other):
        """ Disable default compare method """
        msg = "Implement __cmp__ in class '%s'" % type(self)
        raise NotImplementedError(msg)

    def __hash__(self):
        """ Disable default hashing method """
        msg = "Implement __hash__ in class '%s'" % type(self)
        raise NotImplementedError(msg)


class EqualityObject(BaseObject):
    """
    Base class with support for logical equivalence. By default it handles some
    simple cases (object identity and objects of different classes). To
    implement logical equivalence notion, override L{_equals} function.
    """

    def __eq__(self, other):
        """
        Compare two objects with each other for logical equivalence.
        This method catches some simple cases only. Override the L{_equals}
        method to implement your own logical equivalence notion.
        """
        if self is other:
            return True

        if other.__class__ is not self.__class__:
            return False

        return self._equals(other)


    def __ne__(self, other):
        """
        Compare two objects with each other for logical non-equivalence.
        This method catches some simple cases only. Override the L{_equals}
        method to implement your own logical non-equivalence notion.
        """
        if self is other:
            return False

        if other.__class__ is not self.__class__:
            return True

        return not self._equals(other)

    def _equals(self, other):
        """
        Override to define logical object equivalence. L{other} is a different
        object of the same class.

        Object equivalence should be tested with the normal C{==} and C{!=}
        operators.

        @return: Logical equivalence
        @rtype: C{bool}
        """
        msg = "Implement _equals in class '%s'" % type(self)
        raise NotImplementedError(msg)


class ReadOnlyObject(BaseObject):
    """
    A base object for a read-only class (members cannot be assigned directly,
    instead use the L{self._set_value} function).

    When deriving from this class, the L{self._set_value} function should only
    be called from the constructor of the class. At no time after the
    construction of the instance, should any member variable be changed. This
    is why it's a read only object.
    """
    def __setattr__(self, name, value):
        msg = "It is not allowed to change the value of an attribute in " \
              "class '%s'" % type(self)
        raise ValueError(msg)

    def _set_value(self, name, value):
        """
        Set an attribute to it's value.

        @param name: The name of the attribute.
        @type  name: C{str}

        @param value: The value of the attribute.
        @type  value: C{anything}
        """
        self.__dict__[name] = value



class ReadOnlyStateObject(ReadOnlyObject):
    """
    A base object for a class with read-only state. This is the same as
    L{ReadOnlyObject}, except that non-state members (like cache) may be
    assigned new values at any time (even outside of the constructor). State
    members are those members that are usually compared in the equality
    function L{EqualityObject._equals} and are part of the hash. Note that
    except for the name of this class, there is no implementation difference
    with L{ReadOnlyObject}.
    """



class EqualityReadOnlyObject(EqualityObject, ReadOnlyObject):
    """
    Base class with both equality hooks and read-only of members.
    """



class EqualityReadOnlyStateObject(EqualityObject, ReadOnlyStateObject):
    """
    Base class with both equality hooks and read-only of state members.
    """




def hashObject(obj):
    """
    Hashes an object. This generic hashing function takes lists, tuples,
    sets, frozensets, and dicts into account.

    @param obj: The object to hash.
    @type  obj: C{object}

    @return: The computed hash.
    @rtype:  C{int}
    """
    if type(obj) in (list, tuple, set, frozenset):
        # Note that C{xor} is commutative and associative, so the order of
        # xor-ing values from a sequence does not matter.
        h = 0
        for item in obj:
            h ^= hashObject(item)
        return h

    elif type(obj) is dict:
        # Note that C{xor} is commutative and associative, so the order of
        # xor-ing values from a sequence does not matter.
        h = 0
        for key, value in obj.iteritems():
            h ^= hashObject(key) ^ hashObject(value)
        return h

    else:
        return hash(obj)

