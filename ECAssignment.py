# -*- coding: utf-8 -*-
# $Id$
#
# Copyright (c) 2005 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECAssignmentBox.

from urllib import quote
import re

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.CMFCore import permissions

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
            description = "The answer for this assignment",
            description_msgid = "help_answer",
            label = "Answer",
            label_msgid = "label_answer",
            i18n_domain = I18N_DOMAIN,
            macro = 'answer_widget',
        ),
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
        widget=StringWidget(
            label = 'Grade',
            description = "The grade awarded for this assignment",
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
    # FIXME: use a constant for 'supersede' which should be imported from config
    def manage_afterAdd(self, item, container):
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
        """Return the file contents as plain text.
        Cf. <http://www.bozzi.it/plone/>,
        <http://plone.org/Members/syt/PortalTransforms/user_manual>;
        see also portal_transforms in the ZMI for available
        transformations."""
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
        return None


registerATCT(ECAssignment, PROJECTNAME)
