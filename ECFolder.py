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

    def collect(self):
        folders = self.contentValues(filter={'portal_type': ('ECFolder')})
        students = self.summarizeByStudent()

        wtool = self.portal_workflow
        students['_wfstates'] = wtool.getWorkflowById('ec_assignment_workflow').states.keys()
        
        for folder in folders:
            sum = folder.summarizeByStudent()
            for student in sum.keys():
                if student in students:
                    i = 0
                    for i in range(len(sum[student]) - 1):
                        students[student][i] += sum[student][i]
                else:
                    students[student] = sum[student]
                
            
        return students

    def summarizeByStudent(self):
        boxes = self.contentValues(filter={'portal_type':
                                           ('ECAssignmentBox',
                                            'ECAssignmentBoxQC')})
        students = {}
        wtool = self.portal_workflow
        wf_states = wtool.getWorkflowById('ec_assignment_workflow').states.keys()
        n_states = len(wf_states)
        
        if '_boxes' not in students:
            students['_boxes'] = [0 for i in range(n_states)]

        for box in boxes:
            students['_boxes'][0] += 1
            boxsummary = box.getAssignmentsSummary()
            
            for assignment in boxsummary:
                if assignment.Creator() not in students:
                    students[assignment.Creator()] = [0 for i in range(n_states)]
                students[assignment.Creator()][wf_states.index(wtool.getInfoFor(assignment, 'review_state', ''))] += 1

        return students


    actions = (
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

        {
        'action':      "string:$object_url/by_student",
        'id':          'by_student',
        'name':        'By Student',
        'permissions': (permissions.View,),
        },
    )

registerType(ECFolder)
