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

    def summarize(self, published=True):
        wtool = self.portal_workflow
        items = self.contentValues(filter={'portal_type': 
                                            self.allowed_content_types})

        wf_states = self.getWfStates()
        n_states = len(wf_states)
        students = {}
        
        for item in items:
            if published:
                review_state = wtool.getInfoFor(item, 'review_state')
                if review_state not in ('published'):
                    continue
            if item.portal_type == 'ECFolder':
                sum = item.summarize(published)

                for student in sum.keys():
                    if student in students:
                        i = 0
                        for i in range(len(sum[student]) - 1):
                            students[student][i] += sum[student][i]
                    else:
                        students[student] = sum[student]

            elif self.ecab_utils.isAssignmentBoxType(item):
                boxsummary = item.getAssignmentsSummary()
                
                for assignment in boxsummary:
                    if assignment.Creator() not in students:
                        students[assignment.Creator()] = [0 for i
                                                          in range(n_states)]
                    students[assignment.Creator()][wf_states.index(
                        wtool.getInfoFor(assignment, 'review_state', ''))] += 1
        
        return students
    
    def rework(self, dict):
        array = []
        mtool = self.portal_membership

        for key in dict:
            #array.append((key, util.getFullNameById(self, key), dict[key]))
            array.append((key, self.ecab_utils.getFullNameById(key), dict[key]))
            
            
        array.sort(lambda a, b: cmp(a[1], b[1]))
        return array

    def getWfStates(self):
        wtool = self.portal_workflow
        return wtool.getWorkflowById('ec_assignment_workflow').states.keys()

    def countContainedBoxes(self, published=True):
        """Count the assignment boxes contained in this folder and its
        subfolders.  By default, only published boxes and folders are
        considered.  Set published=False to count all boxes.
        """
        n_boxes = 0
        wtool = self.portal_workflow
        items = self.contentValues(filter={'portal_type':
                                            self.allowed_content_types})

        for item in items:
            if published:
                review_state = wtool.getInfoFor(item, 'review_state')
                if review_state not in ('published'):
                    continue
            if item.portal_type == 'ECFolder':
                n_boxes += item.countContainedBoxes(published)
            elif self.ecab_utils.isAssignmentBoxType(item):
                n_boxes += 1
        
        return n_boxes

    ###########################################################################

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
