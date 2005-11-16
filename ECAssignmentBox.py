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

from Products.ECAssignmentBox.config import I18N_DOMAIN, TEXT_TYPES
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
        default_output_type = 'text/html',
        default_content_type = 'text/structured',
        allowable_content_types = TEXT_TYPES,
        widget=RichWidget(
            label = 'Assignment text',
            label_msgid = 'label_assignment_text',
            description = 'Enter text and hints for the assignment.',
            description_msgid = 'help_assignment_text',
            i18n_domain = I18N_DOMAIN,
            rows=12,
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

    BooleanField(
        'mark_assigned',
        searchable = True,
        widget=BooleanWidget(
            label = 'Mark assigned',
            label_msgid = 'label_mark_assigned',
            description = ('Indicate whether or not marks are assigned '
                           'for the assignment.'),
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

    def getAssignmentsSummary(self):
        items = self.contentValues(filter={'portal_type':
                                           self.allowed_content_types})
        items.sort(lambda a, b: cmp(a.CreationDate(), b.CreationDate()))
        wtool = self.portal_workflow
        current_user = self.portal_membership.getAuthenticatedMember()
        summary = []
        
        for item in items:
            if (current_user.checkPermission('View', item)):
                x = self.contentValues(filter = {'Creator': item.Creator()})
                if len(x) > 1:
                    x.sort(lambda a, b: cmp(a.CreationDate(), b.CreationDate()))
                    summary.append(x[0])
                else:
                    summary.append(item)
        
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
