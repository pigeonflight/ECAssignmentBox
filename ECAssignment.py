# -*- coding: utf-8 -*-
# $Id$
#
# Copyright (c) 2005 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECAssignmentBox.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.CMFCore import CMFCorePermissions

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

from config import PROJECTNAME, ICONMAP, TEXT_TYPES, I18N_DOMAIN
from urllib import quote
import re


# alter default fields -> hide title and description
localBaseSchema = ATContentTypeSchema.copy()
localBaseSchema['title'].default_method = '_generateTitle'

localBaseSchema['title'].widget.visible = {
    'view' : 'invisible',
    'edit' : 'invisible'
}

localBaseSchema['description'].widget.visible = {
    'view' : 'invisible',
    'edit' : 'invisible'
}


# define schema
ECAssignmentSchema = localBaseSchema + Schema((
#    DateTimeField(
#        'datetime',
#        widget = ComputedWidget(
#            label = 'Datetime',
#            label_msgid = 'label_datetime',
#            description = 'The date and time for this submission.',
#            description_msgid = 'help_datetime',
#            i18n_domain = I18N_DOMAIN,
#        ),   
#    ),
#    TextField(
#        'source',
#        searchable = True,
#        default_output_type = 'text/structured',
#        widget = ComputedWidget(
#            label = 'Answer',
#            label_msgid = 'label_answer',
#            description = 'The answer for this assignment.',
#            description_msgid = 'help_source',
#            i18n_domain = I18N_DOMAIN,
#        ),
#    ),

    FileField(
        'file',
        searchable = True,
        primary = True,
        widget = FileWidget(
            description = "The answer for this assignment.",
            description_msgid = "help_answer",
            label = "Answer",
            label_msgid = "label_answer",
            i18n_domain = I18N_DOMAIN,
        ),
    ),

    TextField(
        'feedback',
        searchable = True,
        default_content_type = 'text/structured',
        default_output_type = 'text/html',
        allowable_content_types = TEXT_TYPES,
        widget = TextAreaWidget(
            label = "Manual feedback",
            label_msgid = "label_feedback",
            description = "The marker's feedback for this assignment.",
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
            description = "The grade awarded for this assignment.",
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
    meta_type = "ECAssignment"
    archetype_name = "Assignment"

    default_view   = 'assignment_view'
    immediate_view = 'assignment_view'

    content_icon = "sheet-16.png"
    global_allow = False

    security.declarePrivate('manage_afterAdd')
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


    #security.declarePublic('setField')
    def setField(self, name, value, **kw):
        """TODO: add useful comments"""
        field = self.getField(name)
        field.set(self, value, **kw)


    security.declarePrivate('_generateTitle')
    def _generateTitle(self):
        return self.getCreatorFullName()


    def getCreatorFullName(self):
        #return util.getFullNameById(self, self.Creator())
        return self.ecab_utils.getFullNameById(self.Creator())

    
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

        try:
            result = ptTool.convertTo('text/plain-pre', str(f.get(self)),
                                      mimetype=mt)
        except TransformException:
            result = None
            
        if result:
            return result.getData()
        else:
            return None
            

    actions = updateActions(ATCTContent,
                            HistoryAwareMixin.actions)


    aliases = updateAliases(ATCTContent, {
        'view': 'assignment_view',
        'edit': 'assignment_edit',
        })


registerATCT(ECAssignment, PROJECTNAME)
