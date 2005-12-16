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

from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.base import updateActions, updateAliases
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.ATContentTypes.content.folder import ATFolder

from Products.ECAssignmentBox.config \
     import I18N_DOMAIN, TEXT_TYPES, PROJECTNAME
from Products.ECAssignmentBox.ECAssignmentBox import ECAssignmentBox
from Products.ECAssignmentBox.validators import *
from Products.validation import validation

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import setDefaultRoles
from Products.CMFDynamicViewFTI.permissions import ModifyViewTemplate


isPositive = PositiveNumberValidator("isPositive")
validation.register(isPositive)

localSchema = Schema((
    LinesField(
        'completedStates',
        searchable = False,
        vocabulary = 'getWfStates',
        multiValued = True,
        widget = MultiSelectionWidget(
            label = "Completed States",
            label_msgid = "label_completed_states",
            description = "States considered as completed.",
            description_msgid = "help_completed_states",
            i18n_domain = I18N_DOMAIN,
        ),
    ),

    IntegerField(
        'projectedAssignments',
        searchable = False,
        required = True,
        default = 0,
        validators = ('isInt', 'isPositive'),
        widget = IntegerWidget(
            label = "Projected Number of Assignments",
            label_msgid = "label_projected_assignments",
            description = "Projected number of assignments.",
            description_msgid = "help_projected_assignments",
            i18n_domain = I18N_DOMAIN,
        ),
    ),

))

ECFolderSchema = ATFolderSchema.copy() + localSchema
finalizeATCTSchema(ECFolderSchema, folderish=True, moveDiscussion=False)

class ECFolder(ATFolder):
    """A simple folderish archetype for holding ECAssignments"""

    schema = ECFolderSchema
    
    content_icon = "folder-box-16.png"
    portal_type = meta_type = "ECFolder"
    archetype_name = "ECFolder"
    default_view = 'view_all_boxes'
    immediate_view = 'view_all_boxes'
    suppl_views = () #('all_assignments', 'by_student',)
    allowed_content_types = []

    __implements__ = (ATFolder.__implements__,)

    security = ClassSecurityInfo()

#     security.declarePrivate('manage_afterAdd')
#     def manage_afterAdd(self, item, container):
#         ATFolder.manage_afterAdd(self, item, container)
#         self.manage_permission(ModifyViewTemplate,
#                                roles=['Authenticated'],
#                                acquire=True)
    
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
            array.append((key, self.ecab_utils.getFullNameById(key), dict[key]))
            array.sort(lambda a, b: cmp(a[1], b[1]))

        return array

    def summarizeCompletedAssignments(self, summary=None):
        """Returns a dictionary containing the number of assignments
        in a completed state per student"""
        if not self.completedStates:
            return None

        if not summary:
            summary = self.summarize()
        
        states = self.getWfStates()
        retval = {}

        for student in summary.keys():
            state_no = 0
            retval[student] = 0

            for num in summary[student]:
                if states[state_no] in self.completedStates and num > 0:
                    retval[student] += num
                state_no += 1
        return retval

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

    actions = updateActions(ATFolder, (
        {
        'action':      "string:$object_url/all_assignments",
        'id':          'all_assignments',
        'name':        'Assignments',
        'permissions': (permissions.View,),
        },

        {
        'action':      "string:$object_url/by_student",
        'id':          'by_student',
        'name':        'Statistics',
        'permissions': (permissions.View,),
        },
   ))
    
    aliases = updateAliases(ATFolder, {
        'view': 'view_all_boxes',
        })


registerATCT(ECFolder, PROJECTNAME)
