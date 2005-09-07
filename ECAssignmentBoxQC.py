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
from Products.ECAssignmentBox.ECAssignmentQC import ECAssignmentQC


AssignmentBoxSchema = Schema((
    TextField(
        'description',
        searchable = True,
        default_content_type = 'text/plain',
        default_output_type = 'text/html',
        widget = TextAreaWidget(
            label = "Description",
            label_msgid = "label_description",
            description = "Enter a brief description of the assignment.",
            description_msgid = "help_description",
            i18n_domain = I18N_DOMAIN,
            rows = 5,
        ),
    ),

    TextField(
        'assignment_text',
        default_output_type='text/html',
        default_content_type='text/structured',
        allowable_content_types=('text/plain', 'text/structured', 'text/html',) ,
        widget=RichWidget(
            label='Assignment text',
            label_msgid='label_assignment_text',
            description='Enter text and hints for the assignment.',
            description_msgid='help_assignment_text',
            i18n_domain = I18N_DOMAIN,
            rows=12,
        ),
    ),
    
    TextField(
        'model_solution',
        widget=TextAreaWidget(
            label='Model solution',
            label_msgid='label_model_solution',
            description='Enter a model solution.',
            description_msgid='help_model_solution',
            i18n_domain = I18N_DOMAIN,
        ),   
    ),
    
    TextField(
        'qc_property',
        widget=TextAreaWidget(
            label='QuickCheck properties',
            label_msgid='label_qc_property',
            description='Enter one or more QuickCheck properties. #Model# ' + \
                'will be replaced with the model solution module name and ' + \
                '#Student# will be replaceed with the students\' solution ' + \
                'module.',
            description_msgid='help_qc_property',
            i18n_domain = I18N_DOMAIN,
        )    
    ),
))

class ECAssignmentBoxQC(BaseFolder, OrderedBaseFolder):
    """A simple folderish archetype for holding ECAssignments"""

    security = ClassSecurityInfo()

    __implements__ = (BaseFolder.__implements__, OrderedBaseFolder.__implements__, )

    _at_rename_after_creation = True

    schema = BaseFolder.schema + AssignmentBoxSchema
    filter_content_types = 1
    allowed_content_types = [ECAssignmentQC.meta_type]
    meta_type = "ECAssignmentBoxQC"
    archetype_name = "AssignmentBox (Haskell QuickCheck)"
    content_icon = "box-16.png"            

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
        'action':      "string:$object_url/assignmentbox_view",
        'category':    "object",
        'id':          'view',
        'name':        'View',
        'permissions': ("View",),
        'condition'  : 'python:1'
        },

        {
        'action':      "string:$object_url/assignmentbox_submissions",
        'category':    "object",
        'id':          'assignments',
        'name':        'Assignments',
        'permissions': ("View",),
        'condition'  : 'python:1'
        },
    )

registerType(ECAssignmentBoxQC)
