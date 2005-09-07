# -*- coding: utf-8 -*-
# $Id$
#
# Copyright (c) 2005 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECAssignmentBox.

__author__    = '''ma <amelung@iws.cs.uni-magdeburg.de>'''
__docformat__ = 'plaintext'
__version__   = '$Revision$'

import os, os.path

import ECAssignmentWorkflow

from Globals import package_home

from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory

from config import SKINS_DIR, GLOBALS, PROJECTNAME
from config import ADD_CONTENT_PERMISSION

registerDirectory(SKINS_DIR, GLOBALS)

def initialize(context):
    # Import Types here to register them
    #import ECAssignmentBox, ECAssignmentBoxQC, ECAssignment, ECAssignmentQC
    import ECAssignmentBox, ECAssignmentBoxQC

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)
    
    utils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)

