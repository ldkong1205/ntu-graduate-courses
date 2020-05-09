#
# $Id: maxplus.py 699 2010-04-06 08:05:44Z hat $
#
"""
Basic max+ algebra module.

Values are L{EPSILON}, L{INFINITE}, C{int}, or C{float}.
"""
from automata import baseobjects

class Infinity(baseobjects.BaseObject):
    """
    Class representing infinity.
    """

    def __str__(self):
        return "+inf"

    def __repr__(self):
        return "Infinity()"

class NegInfinity(baseobjects.BaseObject):
    """
    Class representing -infinity.
    """

    def __str__(self):
        return "-inf"

    def __repr__(self):
        return "NegInfinity()"

INFINITE = Infinity()
EPSILON = NegInfinity()

def otimes(aval, bval):
    """
    Compute $aval \otimes bval$ (= aval + bval)

    @param aval: First value to add.
    @type  aval: L{INFINITE}, L{EPSILON}, C{int}, or C{float}

    @param aval: Second value to add.
    @type  aval: L{INFINITE}, L{EPSILON}, C{int}, or C{float}

    @return: The multiplied value.
    @rtype:  L{INFINITE}, L{EPSILON}, C{int}, or C{float}
    """
    if aval is INFINITE or bval is INFINITE:
         return INFINITE

    if aval is EPSILON or bval is EPSILON:
         return EPSILON

    return aval + bval

def oplus(aval, bval):
    """
    Compute $aval \oplus bval$ (= max(aval, bval))

    @param aval: First value to add.
    @type  aval: L{INFINITE}, L{EPSILON}, C{int}, or C{float}

    @param aval: Second value to add.
    @type  aval: L{INFINITE}, L{EPSILON}, C{int}, or C{float}

    @return: The added value.
    @rtype:  L{INFINITE}, L{EPSILON}, C{int}, or C{float}
    """
    if aval is EPSILON:
        return bval
    if bval is EPSILON:
        return aval
    if aval is INFINITE or bval is INFINITE:
        return INFINITE
    return max(aval, bval)

def minimum(aval, bval):
    """
    Return smallest value.

    @param aval: First value to consider.
    @type  aval: L{INFINITE}, L{EPSILON}, C{int}, or C{float}

    @param aval: Second value to consider.
    @type  aval: L{INFINITE}, L{EPSILON}, C{int}, or C{float}

    @return: Smallest value.
    @rtype:  L{INFINITE}, L{EPSILON}, C{int}, or C{float}
    """
    if aval is INFINITE:
        return bval
    if bval  is INFINITE:
        return aval
    if aval is EPSILON or bval is EPSILON:
        return EPSILON
    return min(aval, bval)

def equal(aval, bval):
    """
    Compare two max+ values, return whether L{aval} == L{bval}.

    @param aval: First value to compare.
    @type  aval: L{INFINITE}, L{EPSILON}, C{int}, or C{float}

    @param aval: Second value to compare.
    @type  aval: L{INFINITE}, L{EPSILON}, C{int}, or C{float}

    @return: Whether the first value is equal to the second value.
    @rtype:  C{bool}
    """
    if aval is EPSILON:
        return bval is EPSILON
    if bval is EPSILON:
        return False # aval is definitely not EPSILON.

    if aval is INFINITE:
        return bval is INFINITE
    if bval is INFINITE:
        return False # aval is definitely not INFINITE.

    return aval == bval

def lessthan(aval, bval):
    """
    Compare two max+ values, return whether L{aval} < L{bval}.

    @param aval: First value to compare.
    @type  aval: L{INFINITE}, L{EPSILON}, C{int}, or C{float}

    @param aval: Second value to compare.
    @type  aval: L{INFINITE}, L{EPSILON}, C{int}, or C{float}

    @return: Whether first value is less than second value.
    @rtype:  C{bool}
    """
    if aval is EPSILON:
        return bval is not EPSILON
    if bval is EPSILON:
        return False

    if bval is INFINITE:
        return aval is not INFINITE
    if aval is INFINITE:
        return False

    return aval < bval

def biggerthan(aval, bval):
    """
    Compare two max+ values, return whether L{aval} > L{bval}.

    @param aval: First value to compare.
    @type  aval: L{INFINITE}, L{EPSILON}, C{int}, or C{float}

    @param aval: Second value to compare.
    @type  aval: L{INFINITE}, L{EPSILON}, C{int}, or C{float}

    @return: Whether first value is bigger than second value.
    @rtype:  C{bool}
    """
    if bval is EPSILON:
        return aval is not EPSILON
    if aval is EPSILON:
        return False

    if aval is INFINITE:
        return bval is not INFINITE
    if bval is INFINITE:
        return False

    return aval > bval


class MaxplusCollection(baseobjects.EqualityObject):
    """
    Base class for a vector/matrix collection of max+ values.
    """
    def __str__(self):
        return str(self.dump())


class Vector(MaxplusCollection):
    """
    Generic vector of max+ values.

    @ivar data: Data of the collection.
    @type data: C{list} of (L{INFINITE}, L{EPSILON}, C{int}, or C{float})
    """
    __slots__ = ['data']
    def __init__(self, data):
        self.data = data

    def _equals(self, other):
        if len(self.data) != len(other.data):
            return False
        for aval, bval in zip(self.data, other.data):
            if not equal(aval, bval):
                return False
        return True

    def __hash__(self):
        hval = 0
        for val in self.data:
            hval = hval ^ hash(val)
        return hval

    def length(self):
        return len(self.data)

    def dump(self):
        return tuple(self.data)

    # XXX Is this actually used?
    def set(self, pos, val):
        self.data[pos] = val

    # XXX Is this actually used?
    def get(self, pos):
        return self.data[pos]

class Matrix(MaxplusCollection):
    """
    Generic 2D rectangular max+ value collection.

    @ivar num_row: Number of rows.
    @type num_row: C{int}

    @ivar num_col: Number of columns.
    @type num_col: C{int}

    @ivar data: 2D collection of max+ valus, ordered by row.
    @type data: C{list} of rows, where a row is a C{list} of (L{INFINITE},
                L{EPSILON}, C{int}, or C{float})
    """
    __slots__ = ['num_row', 'num_col', 'data']
    def __init__(self, data):
        self.num_row = len(data)
        self.num_col = len(data[0])
        self.data = data

    def _equals(self, other):
        if self.num_row != other.num_row \
                or self.num_col != other.num_col:
            return False
        for row in range(self.num_row):
            for sv, ov in zip(self.data[row], other.data[row]):
                if not equal(sv, ov):
                    return False
        return True

    def __hash__(self):
        hval = 0
        for row in self.data:
            for val in row:
                hval = hval ^ hash(val)
        return hval

    def dump(self):
        return tuple(tuple(row) for row in self.data)

    # XXX Is this actually used?
    def set(self, rnum, cnum, val):
        self.data[rnum][cnum] = val

    # XXX Is this actually used?
    def get(self, rnum, cnum):
        return self.data[rnum][cnum]

    def get_scalar(self):
        assert self.num_row == 1
        assert self.num_col == 1
        return self.data[0][0]


class RowMatrix(Matrix):
    """
    Matrix consisting of a single row.
    """
    def __init__(self, data):
        """
        @param data: Sequence of values.
        @type  data: C{list} of (L{INFINITE}, L{EPSILON}, C{int}, or C{float})
        """
        Matrix.__init__(self, [data])

class ColumnMatrix(Matrix):
    """
    Matrix consisting of a single column.
    """
    def __init__(self, data):
        """
        @param data: Sequence of values.
        @type  data: C{list} of (L{INFINITE}, L{EPSILON}, C{int}, or C{float})
        """
        Matrix.__init__(self, [[v] for v in data])


def make_vector(def_value, length):
    """
    Construct a vector.

    @param def_value: Default value of the fields.
    @type  def_value: C{int}, or L{EPSILON}

    @param length: Number of elements in the vector.
    @type  length: C{int}

    @return: Vector.
    @rtype:  L{Vector}
    """
    return Vector([def_value] * length)


def make_matrix(def_value, num_row, num_col):
    """
    Construct a max-plus matrix with L{num_row} rows and L{num_col} of values
    initialized to L{def_value}.

    @param num_row: Number of rows of the matrix.
    @type  num_row: C{int}

    @param num_col: Number of columns of the matrix.
    @type  num_col: C{int}

    @param def_value: Default value of the fields.
    @type  def_value: C{int}, or L{EPSILON}

    @return: Matrix.
    @rtype:  L{Matrix}
    """
    data = [[def_value] * num_col for _ in range(num_row)]
    return Matrix(data)

def make_rowmat(def_value, length):
    """
    Construct a max-plus row matrix with L{length} values initialized to
    L{def_value}.

    @param def_value: Default value of the fields.
    @type  def_value: C{int}, or L{EPSILON}

    @param length: Number of columns of the matrix.
    @type  length: C{int}

    @return: Matrix.
    @rtype:  L{Matrix}
    """
    data = [def_value] * length
    return RowMatrix(data)

# XXX Is this actually used?
def make_colmat(def_value, length):
    """
    Construct a max-plus column matrix with L{length} values initialized to
    L{def_value}.

    @param def_value: Default value of the fields.
    @type  def_value: C{int}, or L{EPSILON}

    @param length: Number of rows of the matrix.
    @type  length: C{int}

    @return: Matrix.
    @rtype:  L{Matrix}
    """
    data = [def_value] * length
    return ColumnMatrix(data)



#def vec_to_rowmat(vec):
#    """
#    Convert a vector to a row matrix (horizontal matrix of one row).
#
#    @param vec: Vector to convert.
#    @type  vec: L{Vector}
#
#    @return: Row matrix.
#    @rtype:  L{Matrix}
#    """
#    assert isinstance(vec, Vector)
#    return Matrix([vec.data[:]])

def vec_to_colmat(vec):
    """
    Convert a vector to a column matrix (vertical matrix of one column).

    @param vec: Vector to convert.
    @type  vec: L{Vector}

    @return: Column matrix.
    @rtype:  L{Matrix}
    """
    assert isinstance(vec, Vector)
    return Matrix([[val] for val in vec.data])

def colmat_to_vec(mat):
    """
    Convert a column matrix back to a vector.

    @param mat: Column matrix to convert.
    @type  mat: L{Matrix}

    @return: Converted vector.
    @rtype:  L{Vector}
    """
    assert mat.num_col == 1
    return Vector([val[0] for val in mat.data])


def otimes_appl(nvec, nmat):
    """
    Perform matrix application in max-plus.

    @param nvec: Vector to use.
    @type  nvec: L{Vector}

    @param nmat: Matrix.
    @type  nmat: L{Matrix}

    @return: Result of the L{nmat}(L{nvec}) operation.
    @rtype:  L{Vector}
    """
    assert isinstance(nvec, Vector)
    assert isinstance(nmat, Matrix)
    assert nvec.length() == nmat.num_col

    data = []
    for i in range(nmat.num_row):
        cvar = EPSILON
        for j in range(nmat.num_col):
            cvar = oplus(cvar, otimes(nvec.data[j], nmat.data[j][i]))
        data.append(cvar)
    return Vector(data)


def otimes_mat_mat(anmat, bnmat):
    """
    Perform matrix multiplication.

    @param anmat: Left matrix.
    @type  anmat: L{Matrix}

    @param bnmat: Right matrix.
    @type  bnmat: L{Matrix}

    @return: Resulting matrix.
    @rtype:  L{Matrix}
    """
    assert isinstance(anmat, Matrix)
    assert isinstance(bnmat, Matrix)
    assert anmat.num_col == bnmat.num_row

    res = make_matrix(0, anmat.num_row, bnmat.num_col)
    for rnum in range(anmat.num_row):
        for cvar in range(bnmat.num_col):
            rval = EPSILON
            for evar in range(anmat.num_col):
                rval = oplus(rval, otimes(anmat.data[rnum][evar],
                                          bnmat.data[evar][cvar]))
            res.data[rnum][cvar] = rval
    return res

def otimes_scalar_vec(scal, avector):
    """
    Perform component-wise scalar L{scal} \otimes vector L{avector}.
    """
    res = Vector([otimes(scal, val) for val in avector.data])
    return res

def otimes_vec_vec(avec, bvec):
    """
    Perform component wise vector L{avec} \otimes L{bvec}.
    """
    res = Vector([otimes(aval, bval)
                  for aval, bval in zip(avec.data, bvec.data)])
    return res

def oplus_vec_vec(avec, bvec):
    """
    Perform component wise vector L{avec} \oplus L{bvec}.
    """
    res = Vector([oplus(aval, bval)
                  for aval, bval in zip(avec.data, bvec.data)])
    return res

def oplus_mat_mat(anmat, bnmat):
    """
    Perform component-wise matrix L{anmat} \oplus L{bnmat}.

    @param anmat: First matrix.
    @type  anmat: L{Matrix}

    @param bnmat: Second matrix.
    @type  bnmat: L{Matrix}

    @return: Resulting matrix.
    @rtype:  L{Matrix}
    """
    assert isinstance(anmat, Matrix)
    assert isinstance(bnmat, Matrix)
    assert anmat.num_row == bnmat.num_row
    assert anmat.num_col == bnmat.num_col
    data = [[oplus(aval, bval) for aval, bval in zip(arow, brow)]
                               for arow, brow in zip(anmat.data, bnmat.data)]
    return Matrix(data)


def make_unit_matrix(size):
    """
    Make unit matrix.

    @param size: Size of the unit matrix.
    @type  size: C{int}

    @return: Unit matrix of the requiested size.
    @rtype:  L{Matrix}
    """
    nmat = make_matrix(EPSILON, size, size)
    for idx in range(size):
        nmat.data[idx][idx] = 0

    return nmat

#
# Tests
#

def _otimes_tests():
    assert otimes(EPSILON,  EPSILON ) is EPSILON
    assert otimes(0,        EPSILON ) is EPSILON
    assert otimes(3,        EPSILON ) is EPSILON
    try:
        x = otimes(INFINITE, EPSILON )
    except AssertionError:
        pass
    else:
        assert 0 # Should never get here.

    assert otimes(EPSILON,  0       ) is EPSILON
    assert otimes(0,        0       ) == 0
    assert otimes(3,        0       ) == 3
    assert otimes(INFINITE, 0       ) is INFINITE

    assert otimes(EPSILON,  3       ) is EPSILON
    assert otimes(0,        3       ) == 3
    assert otimes(3,        3       ) == 6
    assert otimes(INFINITE, 3       ) is INFINITE

    try:
        x = otimes(EPSILON,  INFINITE)
    except AssertionError:
        pass
    else:
        assert 0 # Should never get here.
    assert otimes(0,        INFINITE) is INFINITE
    assert otimes(3,        INFINITE) is INFINITE
    assert otimes(INFINITE, INFINITE) is INFINITE

def _oplus_tests():
    assert oplus(EPSILON,  EPSILON ) is EPSILON
    assert oplus(0,        EPSILON ) == 0
    assert oplus(3,        EPSILON ) == 3
    assert oplus(INFINITE, EPSILON ) is INFINITE

    assert oplus(EPSILON,  0       ) == 0
    assert oplus(0,        0       ) == 0
    assert oplus(3,        0       ) == 3
    assert oplus(INFINITE, 0       ) is INFINITE

    assert oplus(EPSILON,  3       ) == 3
    assert oplus(0,        3       ) == 3
    assert oplus(3,        3       ) == 3
    assert oplus(INFINITE, 3       ) is INFINITE

    assert oplus(EPSILON,  INFINITE) is INFINITE
    assert oplus(0,        INFINITE) is INFINITE
    assert oplus(3,        INFINITE) is INFINITE
    assert oplus(INFINITE, INFINITE) is INFINITE

def _minimum_tests():
    assert minimum(EPSILON,  EPSILON ) is EPSILON
    assert minimum(0,        EPSILON ) is EPSILON
    assert minimum(3,        EPSILON ) is EPSILON
    assert minimum(INFINITE, EPSILON ) is EPSILON

    assert minimum(EPSILON,  0       ) is EPSILON
    assert minimum(0,        0       ) == 0
    assert minimum(3,        0       ) == 0
    assert minimum(INFINITE, 0       ) == 0

    assert minimum(EPSILON,  3       ) is EPSILON
    assert minimum(0,        3       ) == 0
    assert minimum(3,        3       ) == 3
    assert minimum(INFINITE, 3       ) == 3

    assert minimum(EPSILON,  INFINITE) is EPSILON
    assert minimum(0,        INFINITE) == 0
    assert minimum(3,        INFINITE) == 3
    assert minimum(INFINITE, INFINITE) is INFINITE

def _equal_tests():
    assert equal(EPSILON,  EPSILON ) == True
    assert equal(0,        EPSILON ) == False
    assert equal(3,        EPSILON ) == False
    assert equal(INFINITE, EPSILON ) == False

    assert equal(EPSILON,  0       ) == False
    assert equal(0,        0       ) == True
    assert equal(3,        0       ) == False
    assert equal(INFINITE, 0       ) == False

    assert equal(EPSILON,  3       ) == False
    assert equal(0,        3       ) == False
    assert equal(3,        3       ) == True
    assert equal(INFINITE, 3       ) == False

    assert equal(EPSILON,  INFINITE) == False
    assert equal(0,        INFINITE) == False
    assert equal(3,        INFINITE) == False
    assert equal(INFINITE, INFINITE) == True

def _lessthan_tests():
    assert lessthan(EPSILON,  EPSILON ) == False
    assert lessthan(0,        EPSILON ) == False
    assert lessthan(3,        EPSILON ) == False
    assert lessthan(INFINITE, EPSILON ) == False

    assert lessthan(EPSILON,  0       ) == True
    assert lessthan(0,        0       ) == False
    assert lessthan(3,        0       ) == False
    assert lessthan(INFINITE, 0       ) == False

    assert lessthan(EPSILON,  3       ) == True
    assert lessthan(0,        3       ) == True
    assert lessthan(3,        3       ) == False
    assert lessthan(INFINITE, 3       ) == False

    assert lessthan(EPSILON,  INFINITE) == True
    assert lessthan(0,        INFINITE) == True
    assert lessthan(3,        INFINITE) == True
    assert lessthan(INFINITE, INFINITE) == False

def _biggerthan_tests():
    assert biggerthan(EPSILON,  EPSILON ) == False
    assert biggerthan(0,        EPSILON ) == True
    assert biggerthan(3,        EPSILON ) == True
    assert biggerthan(INFINITE, EPSILON ) == True

    assert biggerthan(EPSILON,  0       ) == False
    assert biggerthan(0,        0       ) == False
    assert biggerthan(3,        0       ) == True
    assert biggerthan(INFINITE, 0       ) == True

    assert biggerthan(EPSILON,  3       ) == False
    assert biggerthan(0,        3       ) == False
    assert biggerthan(3,        3       ) == False
    assert biggerthan(INFINITE, 3       ) == True

    assert biggerthan(EPSILON,  INFINITE) == False
    assert biggerthan(0,        INFINITE) == False
    assert biggerthan(3,        INFINITE) == False
    assert biggerthan(INFINITE, INFINITE) == False

if __name__ == '__main__':
    _otimes_tests()
    _oplus_tests()
    _minimum_tests()
    _equal_tests()
    _lessthan_tests()
    _biggerthan_tests()


def smaller_mat_mat(anmat, bnmat):
    """
    Perform minimum values of matrix.

    @param anmat: Left matrix.
    @type  anmat: L{Matrix}

    @param bnmat: Right matrix.
    @type  bnmat: L{Matrix}

    @return: Resulting matrix.
    @rtype:  L{Matrix}
    """
    assert isinstance(anmat, Matrix)
    assert isinstance(bnmat, Matrix)
    assert anmat.num_col == 1
    assert bnmat.num_col == 1
    assert anmat.num_row == bnmat.num_row

    res = make_matrix(0, anmat.num_row, anmat.num_col)
    for rnum in range(anmat.num_row):
        t1  = anmat.data[rnum];  t2 = bnmat.data[rnum];
        tt1 = t1[0];             tt2 = t2[0];
        retv = minimum(tt1,tt2);
        res.data[rnum][0] = retv;

    return res
