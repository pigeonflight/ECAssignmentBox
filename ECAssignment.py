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
import time, random, md5, socket

import util

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



#    StringField(
#        'user_id',
#        widget=ComputedWidget(
#            description = "The id of the student submitting this assignment.",
#            label='Student id',
#            description_msgid = 'help_user_id',
#            i18n_domain = I18N_DOMAIN,
#        )
#    ),

# define schema
AssignmentSchema = localBaseSchema + Schema((
    DateTimeField(
        'datetime',
        widget = ComputedWidget(
            label = 'Datetime',
            label_msgid = 'label_datetime',
            description = 'The date and time for this submission.',
            description_msgid = 'help_datetime',
            i18n_domain = I18N_DOMAIN,
        ),   
    ),

    TextField(
        'source',
        searchable = True,
        default_output_type = 'text/structured',
        widget = ComputedWidget(
            label = 'Answer',
            label_msgid = 'label_answer',
            description = 'The answer for this assignment.',
            description_msgid = 'help_source',
            i18n_domain = I18N_DOMAIN,
        ),
    ),

    FileField(
        'file',
        searchable = True,
        widget = FileWidget(
            description = "The uploaded file containing this assignment.",
            description_msgid = "help_file",
            label= "File",
            label_msgid = "label_file",
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
))

finalizeATCTSchema(AssignmentSchema)

class ECAssignment(ATCTContent, HistoryAwareMixin):
    """The ECAssignment class"""

    __implements__ = (ATCTContent.__implements__,
                      IATDocument,
                      HistoryAwareMixin.__implements__,
                     )

    security = ClassSecurityInfo()

    #_at_rename_after_creation = True
    schema = AssignmentSchema
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

#     security.declareProtected(CMFCorePermissions.View, 'index_html')
#     def index_html(self, REQUEST, RESPONSE):
#         """
#         Display the image, with or without standard_html_[header|footer],
#         as appropriate.
#         """
#         return self.file.index_html(REQUEST, RESPONSE)

    #security.declarePublic('setField')
    def setField(self, name, value, **kw):
        """TODO: add useful comments"""
        field = self.getField(name)
        field.set(self, value, **kw)

    security.declarePrivate('_generateTitle')
    def _generateTitle(self):
        return self.getCreatorFullName()

    def getCreatorFullName(self):
        return util.getFullNameById(self, self.Creator())
    
    def getAsPlainText(self):
        """Return the file contents as plain text.
        Cf. <http://www.bozzi.it/plone/>,
        <http://plone.org/Members/syt/PortalTransforms/user_manual>;
        see also portal_transforms in the ZMI for available
        transformations."""
        ptTool = getToolByName(self, 'portal_transforms')
        f = self.getField('file')
        source = ''

        if f:
            mt = self.getContentType('file')
            
            try:
                result = ptTool.convertTo('text/plain-pre', str(f.get(self)),
                                          mimetype=mt)
            except TransformException:
                result = ''
            
            if result:
                return result.getData()
            
            if re.match("text/", mt):
                return f.get(self)
            else:
                return None

    actions = updateActions(ATCTContent,
                            HistoryAwareMixin.actions)

    aliases = updateAliases(ATCTContent, {
        'view': 'assignment_view',
        'edit': 'assignment_edit',
        })

registerATCT(ECAssignment, PROJECTNAME)

# some helper methods

def uuid(*args):
    """
    Generates a universally unique Id. 
    Any arguments only create more randomness.
    
    @params *args
    """
    t = long(time.time() * 1000)
    r = long(random.random()*100000000000000000L)
    try:
        a = socket.gethostbyname(socket.gethostname())
    except:
        # if we can't get a network address, just imagine one
        a = random.random()*100000000000000000L
  
    data = str(t)+' '+str(r)+' '+str(a)+' '+str(args)
    data = md5.md5(data).hexdigest()
    return data

def unique(seq, idfun=None):
    """
    Returns a list with no duplicate items.
    
    @param seq A Sequenz of elements maybe including some duplicte items.
    @return A list without duplicate items.
    """
    if idfun is None:
        def idfun(x): return x

    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result
