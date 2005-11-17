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
from Products.ECAssignmentBox.ECAssignmentQC import ECAssignmentQC


localSchema = Schema((

    StringField(
        'checkerBackend',
        required=True,
        vocabulary = ["haskell_qc"],
        widget = SelectionWidget(
            modes=('edit'),
            label='Checker backend',
            label_msgid='label_checker',
            description='Select a checker backend.',
            description_msgid='help_checker',
            i18n_domain=I18N_DOMAIN,
        ),
    ),
    
    ReferenceField(
        'spoolerConnection',
        allowed_types=('ECSpoolerConnection',),
        multiValued=False,
        relationship='connection',
        required=True,
        #required=True,
        #relationship='subcategories',
        widget = ReferenceWidget(
            modes=('edit'),
            label='Spooler connection',
            label_msgid='label_spooler_connection',
            description='Select a spooler connection.',
            description_msgid='help_spooler_connection',
            i18n_domain=I18N_DOMAIN,
        ),
    ),

    TextField(
        #'modelSource'
        'model_solution',
        widget=TextAreaWidget(
            modes=('edit'),
            label='Model solution',
            label_msgid='label_model_solution',
            description='Enter a model solution.',
            description_msgid='help_model_solution',
            i18n_domain = I18N_DOMAIN,
        ),   
    ),
    
    TextField(
        #'comparatorSource'
        'qc_property',
        required=True,
        widget=TextAreaWidget(
            modes=('edit'),
            label='QuickCheck properties',
            label_msgid='label_qc_property',
            description='Enter one or more QuickCheck properties. #Model# ' + \
                'will be replaced with the model solution module name and ' + \
                '#Student# will be replaceed with the students\' solution ' + \
                'module.',
            description_msgid='help_qc_property',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
))


class ECAssignmentBoxQC(ECAssignmentBox):
    """
    A simple folderish archetype which inherits from ECAssignmentBox and 
    holds ECAssignmentQC objects only.
    
    TODO: generalized version of the box for other programming languages also
    """

    schema = ECAssignmentBox.schema + localSchema
    allowed_content_types = [ECAssignmentQC.meta_type]
    meta_type = "ECAssignmentBoxQC"
    archetype_name = "AssignmentBox (Haskell QuickCheck)"
    content_icon = "box-16.png"            

    # action are inherited from super calls
    # TODO: maybe later we want more or specific actions
#    actions =  (
#        {
#        'action':      "string:$object_url/assignmentbox_view",
#        'category':    "object",
#        'id':          'view',
#        'name':        'View',
#        'permissions': ("View",),
#        'condition'  : 'python:1'
#        },
#    )

registerType(ECAssignmentBoxQC)