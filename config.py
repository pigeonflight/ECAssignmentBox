# -*- coding: utf-8 -*-
# $Id$
#
# Copyright (c) 2005 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECAssignmentBox.

from Products.CMFCore.CMFCorePermissions import AddPortalContent
from Products.Archetypes.public import DisplayList

GLOBALS = globals()

I18N_DOMAIN = 'eduComponents'

# define product and tool names
PROJECTNAME = "ECAssignmentBox"

ECAB_META = "ECAssignmentBox"
ECAB_NAME = "AssignmentBox"

ECA_META = "ECAssignment"
ECA_NAME = "Assignment"


SKINS_DIR = 'skins'

DEPENDENCIES = ['Archetypes',]

TOOL_NAME  = "ecab_utils"
TOOL_TITLE = "ECAssignmentBox Utility Tool"
TOOL_META  = "ECAssignmentBox Utility Tool"

ICONMAP = {'application/pdf' : 'pdf.gif',
           'image'           : 'image_icon.gif'}

ADD_CONTENT_PERMISSION = AddPortalContent

TEXT_TYPES = (
    'text/structured',
    'text/x-rst',
    'text/html',
    'text/plain',
    )


# Some LOG levels
BLATHER=-100
DEBUG=-200
TRACE=-300
    
