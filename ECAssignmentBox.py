# -*- coding: utf-8 -*-
# $Id$
#
# Copyright (c) 2005 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECAssignmentBox.

from DateTime import DateTime

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.CMFCore import permissions

from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.base import updateActions, updateAliases
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.ATContentTypes.content.folder import ATFolder

# local imports
from Products.ECAssignmentBox.config import *
from Products.ECAssignmentBox.ECAssignment import ECAssignment
from Statistics import Statistics

ECAssignmentBoxSchema = ATFolderSchema.copy() + Schema((
    TextField(
        'assignment_text',
        default_output_type = 'text/html',
        default_content_type = 'text/structured',
        allowable_content_types = TEXT_TYPES,
        widget=RichWidget(
            label = 'Assignment text',
            label_msgid = 'label_assignment_text',
            description = 'Enter text and hints for the assignment',
            description_msgid = 'help_assignment_text',
            i18n_domain = I18N_DOMAIN,
            rows=10,
        ),
    ),

    DateTimeField(
        'submission_period_start',
        #mutator = 'setEffectiveDate',
        languageIndependent = True,
        #default=FLOOR_DATE,
        widget = CalendarWidget(
            label = "Start of Submission Period",
            description = ("Date after which students are allowed to "
                           "submit their assignments"),
            label_msgid = "label_submission_period_start",
            description_msgid = "help_submission_period_start",
            i18n_domain = I18N_DOMAIN
        ),
    ),
    
    DateTimeField(
        'submission_period_end',
        #mutator = 'setExpirationDate',
        languageIndependent = True,
        #default=CEILING_DATE,
        widget = CalendarWidget(
            label = "End of Submission Period",
            description = ("Date after which assignments can no longer "
                           "be submitted"),
            label_msgid = "label_submission_period_end",
            description_msgid = "help_submission_period_end",
            i18n_domain = I18N_DOMAIN
        ),
    ),
) # , marshall = PrimaryFieldMarshaller()
)

finalizeATCTSchema(ECAssignmentBoxSchema, folderish=True, moveDiscussion=False)

class ECAssignmentBox(ATFolder):
    """A simple folderish archetype for holding ECAssignments"""

    __implements__ = (ATFolder.__implements__)

    security = ClassSecurityInfo()

    schema = ECAssignmentBoxSchema

    content_icon = "box-16.png"
    portal_type = meta_type = ECAB_META
    archetype_name = ECAB_NAME

    filter_content_types = 1
    allowed_content_types = [ECAssignment.meta_type]

    suppl_views = None
    default_view = 'ecab_view'
    immediate_view = 'ecab_view'

    # -- actions ---------------------------------------------------------------
    actions = updateActions(ATFolder, (
        {
        'action':      "string:$object_url/ecab_assignments",
        'category':    "object",
        'id':          'assignments',
        'name':        'Assignments',
        'permissions': (permissions.View,),
        'condition'  : 'python:1'
        },
    ))
    
    aliases = updateAliases(ATFolder, {
        'view': 'ecab_view',
        })

    # -- methods ---------------------------------------------------------------
    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):
        BaseFolder.manage_afterAdd(self, item, container)
        OrderedBaseFolder.manage_afterAdd(self, item, container)
        # Add local role 'Reviewer' for the creator so that the
        # creator can change the workflow status of submissions
        # without having to be Manager
        creator = self.Creator()
        roles = list(self.get_local_roles_for_userid(creator))
        if 'Reviewer' not in roles:
            roles.append('Reviewer')
            self.manage_setLocalRoles(creator, roles)

        # Create a user-defined role "ECAssignment Viewer".  This role
        # has the View permission in certain states (defined in
        # ECAssignmentWorkflow).  This can be used for model
        # solutions: (1) Submit an assignment with the model
        # solution. (2) Use the "Sharing" tab to assign the role
        # "ECAssignment Viewer" to the users or groups who should be
        # allowed to view the assignment.
        if 'ECAssignment Viewer' not in self.valid_roles():
            self.manage_defined_roles('Add Role',
                                      {'role': 'ECAssignment Viewer'})

    security.declarePublic('hasExpired')
    def hasExpired(self):
        now = DateTime()
        expiration_date = self.getSubmission_period_end()
        
        if ((expiration_date == None) or (expiration_date > now)):
            return False
        else:
            return True

    security.declarePublic('isEffective')
    def isEffective(self):
        now = DateTime()
        effective_date = self.getSubmission_period_start()

        if ((effective_date != None) and (effective_date > now)):
            return False
        else:
            return True

    security.declarePublic('canResubmit')
    def canResubmit(self):
        user_id = self.portal_membership.getAuthenticatedMember().getId()
        wtool = self.portal_workflow
        
        assignments = self.contentValues(filter = {'Creator': user_id})
        
        for a in assignments:
            wf = wtool.getWorkflowsFor(a)[0]
            if wf.getInfoFor(a, 'review_state', '') != 'superseded' \
                   and not wf.isActionSupported(a, 'supersede'):
                return False
        
        return True

    def getAssignmentsSummary(self, id=None):
        items = self.contentValues(filter={'portal_type':
                                           self.allowed_content_types})
        items.sort(lambda a, b: cmp(a.CreationDate(), b.CreationDate()))
        wtool = self.portal_workflow
        current_user = self.portal_membership.getAuthenticatedMember()
        summary = []
        
        for item in items:
            if (current_user.checkPermission(permissions.View, item)):
                if id and item.Creator() != id:
                    continue
                summary.append(item)
        return summary

    def getNumericGrades(self):
        """
        Add documentation here
        """
        wtool = self.portal_workflow
        items = self.contentValues(filter={'portal_type':
                                           self.allowed_content_types})
        grades = []

        for item in items:
            state = wtool.getInfoFor(item, 'review_state')
            if state not in ('graded'):
                continue
            
            if not item.mark:
                continue

            grades.append(item.mark)

        for i in range(0, len(grades)):
            try:
                grades[i] = float(grades[i])
            except ValueError:
                return None

        return grades

    security.declarePublic('getAverageGrade')
    def getAverageGrade(self):
        """
        Add documentation here
        """
        grades = self.getNumericGrades()

        try:
            stats = Statistics(grades)
        except:
            return None
        
        return stats.mean

    security.declarePublic('getMedianGrade')
    def getMedianGrade(self):
        """
        Add documentation here
        """
        grades = self.getNumericGrades()
        
        try:
            stats = Statistics(grades)
        except:
            return None
        
        return stats.median


registerATCT(ECAssignmentBox, PROJECTNAME)
