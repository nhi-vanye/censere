
from peewee import Expression, OP

def mod(lhs, rhs):
    return Expression(lhs, OP.MOD, rhs)
