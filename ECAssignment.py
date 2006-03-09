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

from urllib import quote
import re

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName

from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.base import updateActions, updateAliases
from Products.ATContentTypes.content.base import translateMimetypeAlias
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATContentTypes.interfaces import IATDocument

# The following two imports are for getAsPlainText()
from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.utils import TransformException

# local imports
from Products.ECAssignmentBox.config import *


# alter default fields -> hide title and description
ECAssignmentSchema = ATContentTypeSchema.copy()
ECAssignmentSchema['title'].default_method = '_generateTitle'

ECAssignmentSchema['title'].widget.visible = {
    'view' : 'invisible',
    'edit' : 'invisible'
}

ECAssignmentSchema['description'].widget.visible = {
    'view' : 'invisible',
    'edit' : 'invisible'
}

# define schema
ECAssignmentSchema = ECAssignmentSchema + Schema((
    FileField(
        'file',
        searchable = True,
        primary = True,
        widget = FileWidget(
            label = "Answer",
            label_msgid = "label_answer",
            description = "The submission for this assignment",
            description_msgid = "help_answer",
            i18n_domain = I18N_DOMAIN,
            macro = 'answer_widget',
        ),
    ),

    TextField(
        'remarks',
        default_content_type = 'text/structured',
        default_output_type = 'text/html',
        allowable_content_types = TEXT_TYPES,
        widget = TextAreaWidget(
            label = "Remarks",
            label_msgid = "label_remarks",
            description = "Your remarks for this assignment (they will not be shown to the student)",
            description_msgid = "help_remarks",
            i18n_domain = I18N_DOMAIN,
            rows = 8,
        ),
        read_permission = permissions.ModifyPortalContent,
    ),

    TextField(
        'feedback',
        searchable = True,
        default_content_type = 'text/structured',
        default_output_type = 'text/html',
        allowable_content_types = TEXT_TYPES,
        widget = TextAreaWidget(
            label = "Feedback",
            label_msgid = "label_feedback",
            description = "The grader's feedback for this assignment",
            description_msgid = "help_feedback",
            i18n_domain = I18N_DOMAIN,
            rows = 8,
        ),
    ),

    StringField(
        'mark',
        searchable = True,
        accessor = 'getGradeIfAllowed',
        edit_accessor = 'getGradeForEdit',
        widget=StringWidget(
            label = 'Grade',
            label_msgid = 'label_grade',
            description = "The grade awarded for this assignment",
            description_msgid = "help_grade",
            i18n_domain = I18N_DOMAIN,
        ),
    ),
  ) # , marshall = PrimaryFieldMarshaller()
)

finalizeATCTSchema(ECAssignmentSchema)


class ECAssignment(ATCTContent, HistoryAwareMixin):
    """A simple assignment"""

    __implements__ = (ATCTContent.__implements__,
                      IATDocument,
                      HistoryAwareMixin.__implements__,
                     )

    security = ClassSecurityInfo()

    #_at_rename_after_creation = True
    schema = ECAssignmentSchema
    meta_type = ECA_META
    archetype_name = ECA_NAME

    content_icon = "sheet-16.png"
    global_allow = False

    default_view   = 'eca_view'
    immediate_view = 'eca_view'

    # -- actions ---------------------------------------------------------------
    actions = updateActions(ATCTContent, (
        {
        'action':      "string:$object_url/eca_grade",
        'category':    "object",
        'id':          'grade',
        'name':        'Grade',
        'permissions': (permissions.ModifyPortalContent,),
        'condition':   'python:1'
        #'condition':   "python: portal.portal_workflow.getInfoFor(here, 'review_state', '') == 'graded'"
        },

        {
        'action':      "string:$object_url/base_edit",
        'category':    "object",
        'id':          'edit',
        'name':        'Edit',
        'permissions': (permissions.ModifyPortalContent,),
        'condition':   "python: here.Creator() == \
            portal.portal_membership.getAuthenticatedMember().getUserName()"
        },

        ))

    aliases = updateAliases(ATCTContent, {
        'view': 'eca_view',
        })

    # -- methods ---------------------------------------------------------------
    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):
        """
        """
        BaseContent.manage_afterAdd(self, item, container)
        
        wtool = self.portal_workflow
        assignments = self.contentValues(filter = {'Creator': item.Creator()})
        if assignments:
            for a in assignments:
                if a != self:
                    wf = wtool.getWorkflowsFor(a)[0]
                    if wf.isActionSupported(a, 'supersede'):
                        wtool.doActionFor(a, 'supersede',
                                          comment='Superseded by %s'
                                          % self.getId())

        self.sendNotificationEmail()
    
    def sendNotificationEmail(self):
        """
        When this assignment is created, send a notification email to
        the owner of the assignment box, unless emailing is turned off.
        """
        portal_url = getToolByName(self, 'portal_url')
        portal = portal_url.getPortalObject()
        portal_language = portal.getProperty('default_language', None)
        portal_qi = getToolByName(self, 'portal_quickinstaller')

        productVersion = portal_qi.getProductVersion(PROJECTNAME)
        box = self.aq_parent
        
        submitterId   = self.Creator()
        submitterName = self.ecab_utils.getFullNameById(submitterId)
        submissionURL = self.ecab_utils.normalizeURL(self.absolute_url())

        addresses = box.getNotificationEmailAddresses()
        prefLang = self.ecab_utils.getUserPropertyById(box.Creator(),
                                                       'language')
        if not prefLang:
            prefLang = portal_language
        
        default_subject = '[${id}] Submission to "${box_title}" by ${student}'
        subject = self.translate(domain='eduComponents',
                                 msgid='email_new_submission_subject',
                                 target_language=prefLang,
                                 mapping={'id': PROJECTNAME,
                                          'box_title': box.Title(),
                                          'student': submitterName},
                                 default=default_subject)

        default_mailText = '${student} has made a submission to ' \
                           'the assignment "${box_title}".\n\n' \
                           '<${url}>\n\n' \
                           '-- \n' \
                           '${product} ${version}'
        mailText = self.translate(domain='eduComponents',
                                  msgid='email_new_submission_content',
                                  target_language=prefLang,
                                  mapping={'box_title': box.Title(),
                                           'student': submitterName,
                                           'url': submissionURL,
                                           'product': PROJECTNAME,
                                           'version': productVersion},
                                  default=default_mailText)

        box.sendNotificationEmail(addresses, subject, mailText)


    # FIXME: deprecated, set security
    def setField(self, name, value, **kw):
        """Sets value of a field"""
        field = self.getField(name)
        field.set(self, value, **kw)


    security.declarePrivate('_generateTitle')
    def _generateTitle(self):
        #log("Title changed from '%s' to '%s'" % \
        #        (self.title, self.getCreatorFullName(),), severity=DEBUG)
        return self.getCreatorFullName()


    # FIXME: set security
    def getCreatorFullName(self):
        #return util.getFullNameById(self, self.Creator())
        return self.ecab_utils.getFullNameById(self.Creator())

    
    # FIXME: deprecated, use get_data or data in page templates
    def getAsPlainText(self):
        """
        Return the file contents as plain text.
        Cf. <http://www.bozzi.it/plone/>,
        <http://plone.org/Members/syt/PortalTransforms/user_manual>;
        see also portal_transforms in the ZMI for available
        transformations.
        
        @return file content as plain text or None
        """
        ptTool = getToolByName(self, 'portal_transforms')
        f = self.getField('file')
        #source = ''

        mt = self.getContentType('file')
        
        if re.match("text/|application/xml", mt):
            return str(f.get(self))
        else:
            return None
        
        # FIXME: cut this for the moment because result of Word or PDF files 
        #        looks realy ugly

        try:
            result = ptTool.convertTo('text/plain-pre', str(f.get(self)),
                                      mimetype=mt)
        except TransformException:
            result = None
            
        if result:
            return result.getData()
        else:
            return None
    
    
    security.declarePublic('evaluate')
    def evaluate(self, parent):
        """
        Will be called if a new assignment is added to this assignment box to
        evaluate it. Please do not confuse this with the validation of the
        input values.
        For ECAssignment this mehtod returns nothing but it can be 
        overwritten in subclasses, e.g. ECAutoAssignmentBox.
        
        @return None
        """
        return None

    
    #security.declarePublic('getGradeIfAllowed')
    def getGradeIfAllowed(self):
        """
        The accessor for field grade. Returns the grade if this assigment is in
        state graded or current user has reviewer permissions.
        
        @return string value of the given grade or nothing
        """
        wtool = self.portal_workflow
        state = wtool.getInfoFor(self, 'review_state', '')
        
        currentUser = self.portal_membership.getAuthenticatedMember()
        isReviewer = currentUser.checkPermission(permissions.ReviewPortalContent, self)

        if self.mark:
            if state == 'graded':
                return self.mark
            elif isReviewer:
                return '(' + self.mark + ')'


    #security.declarePublic('getGradeForEdit')
    def getGradeForEdit(self):
        """
        The edit_accessor for field grade. Returns the grade for this assignment.
        
        @return string value of the given grade or nothing
        """
        return self.mark
    

    #security.declarePublic('getViewerNames')
    def getViewerNames(self):
        """
        Get the names of the users and/or groups which have the local
        role `ECAssignment Viewer'.  This allows reviewers to quickly
        check who may view an assignment.
        
        @return list of user and/or group names
        """
        principalIds = self.users_with_local_role('ECAssignment Viewer')
        names = []
        
        for id in principalIds:
            if self.portal_groups.getGroupById(id):
                names.append(self.portal_groups.getGroupById(id).getGroupName())
            else:
                names.append(self.ecab_utils.getFullNameById(id))

        return names


registerATCT(ECAssignment, PROJECTNAME)
