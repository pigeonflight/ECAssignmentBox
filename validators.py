# -*- coding: utf-8 -*-
# $Id$
#
# Copyright (c) 2005 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECAssignmentBox.

try:
    from Products.validation.interfaces.IValidator import IValidator
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir))
    from interfaces.IValidator import IValidator
    del sys, os

class PositiveNumberValidator:
    __implements__ = IValidator

    def __init__(self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description
    
    def __call__(self, value, *args, **kwargs):
        try:
            nval = float(value)
        except ValueError:
            return ("Validation failed (%(name)s): could not convert \
            '%(value)r' to number" % { 'name' : self.name, 'value': value})

        if nval >= 0:
            return True

        return ("Validation failed: '%(value)s' is not a positive number." %
                { 'value': value, })
