# -*- coding: utf-8 -*-
# $Id$
#
# Copyright (c) 2005 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of LTAssignmentBox.

from Products.CMFCore.CMFCorePermissions import AddPortalContent
from Products.Archetypes.public import DisplayList

GLOBALS = globals()

PROJECTNAME = "ECAssignmentBox"
I18N_DOMAIN = 'eduComponents'

SKINS_DIR = 'skins'

ICONMAP = {'application/pdf' : 'pdf.gif',
           'image'           : 'image_icon.gif'}

ADD_CONTENT_PERMISSION = AddPortalContent

TEXT_TYPES = (
    'text/structured',
    'text/x-rst',
    'text/html',
    'text/plain',
    )
