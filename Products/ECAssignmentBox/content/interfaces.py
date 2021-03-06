# -*- coding: utf-8 -*-
# $Id$
#
# Copyright (c) 2006-2011 Otto-von-Guericke-UniversitŠt Magdeburg
#
# This file is part of ECAssignmentBox.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'

from zope.interface import Interface

class IECFolder(Interface):
    """Marker interface for .ECFolder.ECFolder
    """

class IECAssignmentBox(Interface):
    """Marker interface for .ECAssignmentBox.ECAssignmentBox
    """

class IECAssignment(Interface):
    """Marker interface for .ECAssignment.ECAssignment
    """
