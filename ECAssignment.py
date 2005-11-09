# -*- coding: utf-8 -*-
# $Id$
#
# Copyright (c) 2005 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECAssignmentBox.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.CMFCore import CMFCorePermissions
# The following two imports are for getAsPlainText()
from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.utils import TransformException
from config import ICONMAP, I18N_DOMAIN
from urllib import quote
import os
import re
import tempfile
import time, random, md5, socket


# resourcestring
REGEX_FAILED = '(?m)Falsifiable, after (\d+) tests?:\n(.*)'
REGEX_PASSED = 'passed (\d+)'
REGEX_LINENUMBER = ':\d+'

DEFAULT_MODEL_MODULE_NAME = '#Model#'
DEFAULT_STUDENT_MODULE_NAME =  '#Student#'


# alter default fields -> hide title and description
localBaseSchema = BaseSchema.copy()
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
        'auto_feedback',
        searchable = True,
        widget = ComputedWidget(
            label = "Auto feedback",
            label_msgid = "label_auto_feedback",
            description = "The automatic feedback for this assignment.",
            description_msgid = "help_auto_feedback",
            i18n_domain = I18N_DOMAIN,
        ),
    ),

    TextField(
        'feedback',
        searchable = True,
        default_content_type = 'text/structured',
        default_output_type = 'text/html',
        allowable_content_types = ('text/structured',
                                   'text/html',
                                   'text/plain',),
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


class ECAssignment(BaseContent):
    """The ECAssignment class"""

    security = ClassSecurityInfo()

    #_at_rename_after_creation = True
    schema = AssignmentSchema
    meta_type = "ECAssignment"
    archetype_name = "Assignment"
    content_icon = "sheet-16.png"
    global_allow = False

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

    def getCreatorFullName(self):
        creator_id = self.Creator()
        creator = self.portal_membership.getMemberById(creator_id)
        return creator.getProperty('fullname', '')

    def getAsPlainText(self):
        """Return the file contents as plain text.
        Cf. <http://www.bozzi.it/plone/>,
        <http://plone.org/Members/syt/PortalTransforms/user_manual>"""
        ptTool = getToolByName(self, 'portal_transforms')
        f = self.getField('file')
        source = ''

        if f:
            mt = self.getContentType('file')
            
            try:
                result = ptTool.convertTo('text/plain', str(f.get(self)),
                                          mimetype=mt)
            except TransformException:
                result = ''
            
            if result:
                return result.getData()
            
            if re.match("text/", mt):
                return f.get(self)
            else:
                return None

    actions = (
        {
        'action':      "string:${object_url}/assignment_view",
        'category':    "object",
        'id':          'view',
        'name':        'View',
        'permissions': ("View",),
        'condition'  : 'python:1'
        },

        {
        'action':      "string:${object_url}/assignment_edit",
        'category':    "object",
        'id':          'edit',
        'name':        'Edit',
        'permissions': ("Edit",),
        'condition'  : 'python:1'
        },
    )

registerType(ECAssignment)

# some hepler methods

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
