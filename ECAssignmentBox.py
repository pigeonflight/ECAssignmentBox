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
from Products.ECAssignmentBox.ECAssignment import ECAssignment



AssignmentBoxSchema = Schema((
    TextField(
        'description',
        searchable = True,
        default_content_type = 'text/plain',
        default_output_type = 'text/plain',
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
    
    BooleanField(
        'mark_assigned',
        searchable = True,
        widget=BooleanWidget(
            label = 'Mark assigned',
            label_msgid = 'label_mark_assigned',
            description = 'Indicate whether or not marks are assigned for the assignment.',
            description_msgid = 'help_mark_assigned',
            i18n_domain = I18N_DOMAIN
        ),
    ),

))

class ECAssignmentBox(BaseFolder, OrderedBaseFolder):
    """A simple folderish archetype for holding ECAssignments"""

    security = ClassSecurityInfo()

    __implements__ = (BaseFolder.__implements__, OrderedBaseFolder.__implements__, )

    _at_rename_after_creation = True

    schema = BaseFolder.schema + AssignmentBoxSchema
    filter_content_types = 1
    allowed_content_types = [ECAssignment.meta_type]
    meta_type = "ECAssignmentBox"
    archetype_name = "AssignmentBox"
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

    def getAssignmentsSummary(self):
        """Return a dictionary, keyed by student name, with
        information about the assignments submitted to an
        AssignmentBox (an array containing the date/time, the workflow
        status and the grade."""
        items = self.contentValues(filter={'portal_type':
                                           self.allowed_content_types})
        wtool = self.portal_workflow
        summary = {}

        for item in items:
            creator = item.Creator()
            date = item.getDatetime()
            if (creator not in summary) or (summary[creator][0] < date):
                summary[creator] = [date,
                                    wtool.getInfoFor(item, 'review_state', ''),
                                    item.getMark()]

        return summary

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

registerType(ECAssignmentBox)
