# -*- coding: utf-8 -*-
# $Id$
#
# Copyright (c) 2005 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECAssignmentBox.

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.atapi import *
from Products.CMFCore import CMFCorePermissions

from Products.ECAssignmentBox.config import I18N_DOMAIN
from Products.ECAssignmentBox.ECAssignmentBox import ECAssignmentBox
from Products.ECAssignmentBox.ECAssignmentBoxQC import ECAssignmentBoxQC



ExerciseSheetSchema = Schema((
    TextField(
        'description',
        searchable = True,
        default_content_type = 'text/plain',
        default_output_type = 'text/html',
        widget = TextAreaWidget(
            label = "Description",
            label_msgid = "label_description",
            description = "Enter a brief description of this exercise sheet.",
            description_msgid = "help_description",
            i18n_domain = I18N_DOMAIN,
            rows = 5,
        ),
    ),

))

class ECExerciseSheet(BaseFolder, OrderedBaseFolder):
    """A simple folderish archetype for holding ECAssignmentBoxs"""

    security = ClassSecurityInfo()

    __implements__ = (BaseFolder.__implements__, OrderedBaseFolder.__implements__, )

    _at_rename_after_creation = True

    schema = BaseFolder.schema + ExerciseSheetSchema
    filter_content_types = True
    allowed_content_types = [ECAssignmentBox.meta_type, ECAssignmentBoxQC.meta_type]
    meta_type = "ECExerciseSheet"
    archetype_name = "ExerciseSheet"
    content_icon = "folder-box-16.png"            

    security.declarePublic('hasExpired')
    def hasExpired(self):
        now = DateTime()
        expiration_date = self.getExpirationDate()
        
        if((expiration_date == None) or (expiration_date > now)):
            return False
        else:
            return True

    security.declarePublic('isEffective')
    def isEffective(self):
        now = DateTime()
        effective_date = self.getEffectiveDate()

        if((effective_date != None) and (effective_date > now)):
            return False
        else:
            return True

    actions =  (
        {
        'action':      "string:$object_url/exercise_sheet_view",
        'category':    "object",
        'id':          'view',
        'name':        'View',
        'permissions': ("View",),
        'condition'  : 'python:1'
        },

    )

registerType(ECExerciseSheet)
