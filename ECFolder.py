# -*- coding: utf-8 -*-
# $Id$
#
# Copyright (c) 2006 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECAssignmentBox.
#
# ECAssignmentBox is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ECAssignmentBox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ECAssignmentBox; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from DateTime import DateTime

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.CMFCore import permissions

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import setDefaultRoles
from Products.CMFDynamicViewFTI.permissions import ModifyViewTemplate

from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.base import updateActions, updateAliases
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.ATContentTypes.content.folder import ATFolder

from Products.validation import validation

# local imports
from Products.ECAssignmentBox.config import *
from Products.ECAssignmentBox.ECAssignmentBox import ECAssignmentBox
from Products.ECAssignmentBox.validators import *


isPositive = PositiveNumberValidator("isPositive")
validation.register(isPositive)

ECFolderSchema = Schema((
    TextField(
        'directions',
        default_content_type = 'text/structured',
        default_output_type = 'text/html',
        allowable_content_types = TEXT_TYPES,
        widget = RichWidget(
            label = 'Directions',
            label_msgid = 'label_directions',
            description = 'Instructions/directions that all assignment boxes in this folder refer to',
            description_msgid = 'help_directions',
            i18n_domain = I18N_DOMAIN,
            rows = 8,
        ),
    ),

    LinesField(
        'completedStates',
        searchable = False,
        vocabulary = 'getWfStatesDisplayList',
        multiValued = True,
        widget = MultiSelectionWidget(
            label = "Completed States",
            label_msgid = "label_completed_states",
            description = "States considered as completed",
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
            description = "Projected number of assignments",
            description_msgid = "help_projected_assignments",
            i18n_domain = I18N_DOMAIN,
        ),
    ),

))

ECFolderSchema = ATFolderSchema.copy() + ECFolderSchema
finalizeATCTSchema(ECFolderSchema, folderish=True, moveDiscussion=False)

class ECFolder(ATFolder):
    """A container for assignment boxes"""

    schema         = ECFolderSchema
    
    content_icon   = "folder-box-16.png"
    portal_type    = meta_type = "ECFolder"
    archetype_name = "ECFolder"
    immediate_view = 'ecfolder_view'
    default_view   = 'ecfolder_view'
    #suppl_views    = () #('all_assignments', 'by_student',)
    allowed_content_types = []

    typeDescription = "A container for assignment boxes."
    typeDescMsgId = 'description_edit_ecf'

    __implements__ = (ATFolder.__implements__,)
    security = ClassSecurityInfo()

    _at_rename_after_creation = True

    # -- actions --------------------------------------------------------------
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
        
        {
        'action':      'string:ecf_modify_boxes:method',
        'id':          'ecf_modify_boxes',
        'name':        'Set Assignment Box Options',
        'permissions': (permissions.ManageProperties,),
        'category':    'folder_buttons',
        },
   ))
    
    aliases = updateAliases(ATFolder, {
        'view': 'ecfolder_view',
        })

    # -- methods --------------------------------------------------------------
#    security.declarePrivate('manage_afterAdd')
#    def manage_afterAdd(self, item, container):
#        ATFolder.manage_afterAdd(self, item, container)
#        self.manage_permission(ModifyViewTemplate,
#                               roles=['Authenticated'],
#                               acquire=True)

    
    #security.declarePrivate('summarize')
    def summarize(self, published=True):
        """
        Returns an dictionary containing summarized states of all assignments 
        for current user - or all users if manager - in all subfolders.  By 
        default, only published boxes and folders are considered.  Set 
        published=False to count all boxes.

        @param published only published boxes and folders are considered
        @return a dictionary containing user-id as key and summarized states
                as value
        """
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
                        for i in range(len(sum[student])):
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

    #security.declarePrivate('summarizeGrades')
    def summarizeGrades(self, published=True):
        """
        Create a dictionary listing all grades for the contained
        assignments by student, i.e., the keys are user IDs, the
        values are lists of grades.  Example:

        {'freddy': [3.0, 3.0], 'dina': [2.0, 2.0, 2.0]}
        
        @return a dictionary
        """
        wtool = self.portal_workflow
        items = self.contentValues(filter={'portal_type': 
                                            self.allowed_content_types})
        students = {}
        
        for item in items:
            if published:
                review_state = wtool.getInfoFor(item, 'review_state')
                if review_state not in ('published'):
                    continue
            
            grades = {}
            
            if item.portal_type == 'ECFolder':
                grades = item.summarizeGrades(published)
            elif self.ecab_utils.isAssignmentBoxType(item):
                grades = item.getGradesByStudent()

            # No grades were assigned--no problem.
            if grades == {}:
                continue
            
            # Non-numeric grades were assigned: Immediately return,
            # as we can't calculate meaningful statistics in this
            # case.
            if grades == None:
                return {}
            
            for student in grades:
                if student not in students:
                    students[student] = []
                if type(grades[student]) is list:
                    students[student].extend(grades[student])
                else:
                    students[student].append(grades[student])
            
        return students
    
    #security.declarePrivate('rework')
    def rework(self, dict):
        """
        @param dict summarize assignments only in published assignment boxes
        @return an array
        """
        array = []
        mtool = self.portal_membership

        for key in dict:
            array.append((key, self.ecab_utils.getFullNameById(key),
                          dict[key]))
            array.sort(lambda a, b: cmp(a[1], b[1]))

        return array


    #security.declarePrivate('FIXME')
    def summarizeCompletedAssignments(self, summary=None):
        """
        Returns a dictionary containing the number of assignments
        in a completed state per student.
        
        @param summary 
        @return a dictionary
        """
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


    #security.declarePrivate('getWfStates')
    def getWfStates(self):
        """
        @deprecated use getWfStates in ecab_utils instead
        """
        utils = self.ecab_utils
        return utils.getWfStates(ECA_WORKFLOW_ID)


    #security.declarePrivate('getWfStatesDisplayList')
    def getWfStatesDisplayList(self):
        """
        @deprecated use getWfStatesDisplayList in ecab_utils instead
        """
        utils = self.ecab_utils
        return utils.getWfStatesDisplayList(ECA_WORKFLOW_ID)


    #security.declarePrivate('getWfTransitionsDisplayList')
    def getWfTransitionsDisplayList(self):
        """
        @deprecated use getWfTransitionsDisplayList in ecab_utils instead
        """
        utils = self.ecab_utils
        return utils.getWfTransitionsDisplayList(ECA_WORKFLOW_ID)


    #security.declarePrivate('countContainedBoxes')
    def countContainedBoxes(self, published=True):
        """
        Count the assignment boxes contained in this folder and its
        subfolders.  By default, only published boxes and folders are
        considered.  Set published=False to count all boxes.

        @param published 
        @return an integer
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


registerATCT(ECFolder, PROJECTNAME)
