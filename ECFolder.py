# -*- coding: utf-8 -*-
# $Id$
#
# Copyright (c) 2005 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECAssignmentBox.

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.atapi import *
from Products.CMFCore import permissions

from Products.ECAssignmentBox.config import I18N_DOMAIN, TEXT_TYPES
from Products.ECAssignmentBox.ECAssignmentBox import ECAssignmentBox

LocalSchema = Schema((
    TextField(
        'description',
        searchable = True,
        default_content_type = 'text/plain',
        default_output_type = 'text/plain',
        widget = TextAreaWidget(
            label = "Description",
            label_msgid = "label_description",
            description = "Enter a brief description of the folder.",
            description_msgid = "help_description",
            i18n_domain = I18N_DOMAIN,
            rows = 5,
        ),
    ),

))

class ECFolder(BaseFolder, OrderedBaseFolder):
    """A simple folderish archetype for holding ECAssignments"""

    security = ClassSecurityInfo()

    __implements__ = (BaseFolder.__implements__, OrderedBaseFolder.__implements__, )

    _at_rename_after_creation = True

    schema = BaseFolder.schema + LocalSchema
    filter_content_types = False
    allowed_content_types = []
    meta_type = "ECFolder"
    archetype_name = "ECFolder"
    content_icon = "folder-box-16.png"

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
        'action':      "string:$object_url/view_all_boxes",
        'id':          'view',
        'name':        'View',
        'permissions': (permissions.View,),
        },

        {
        'action':      "string:$object_url/all_assignments",
        'id':          'all_assignments',
        'name':        'All Assignments',
        'permissions': (permissions.View,),
        },

    )

registerType(ECFolder)
