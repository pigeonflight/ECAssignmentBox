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

    BooleanField(
        'solved',
        searchable = True,
        widget=BooleanWidget(
            label = 'Solved',
            label_msgid = 'label_solved',
            description = 'The solved flag for this assignment.',
            description_msgid = 'help_solved',
            i18n_domain = I18N_DOMAIN
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


class ECAssignmentQC(BaseContent):
    """The ECAssignmentQC class"""

    security = ClassSecurityInfo()

    #_at_rename_after_creation = True
    schema = AssignmentSchema
    meta_type = "ECAssignmentQC"
    archetype_name = "Assignment (Haskell QuickCheck)"
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

    security.declarePublic('evaluate')
    def evaluate(self, modelSource, propertySource):
        """TODO: add some usefull comments"""
#        try:
        # return error message if are not all values set
        if (self.getSource() == None) or (modelSource == None) or \
           (propertySource == None):
            return context.translate(\
                        msgid   = 'evaluation_failed',\
                        domain  = '',\
                        default = 'Some values left unset.')
                

        # write ms, ss and wrapper files
        # 1. model solution file
        mSModuleName = self._getUniqueModuleName('Model')
        mSFileName = self._getTempFileName(mSModuleName)
        mSSource = 'module ' + mSModuleName + ' where\n\n' + modelSource
        self._writeFile(mSSource, mSFileName)
                    
        # 2. students' solution
        sSModuleName = self._getUniqueModuleName('Student')
        sSFileName = self._getTempFileName(sSModuleName)
        sSSource = 'module ' + sSModuleName + ' where\n\n' + self.getSource()
        self._writeFile(sSSource, sSFileName)
        
        # 3. write wrapper and execute
        # get all property names first
        propertyNames = re.findall('prop_\S*', propertySource)
        propertyNames = unique(propertyNames)
        
        # helper variable
        solvedProperties = [];
        
        # for each property write a wrapper 
        for propertyName in propertyNames:
            # 3.1 module definition and imports
            wFileName = self._getTempFileName(self._getUniqueModuleName())
            wSource = 'module Main where\n\n' + \
                      'import QuickCheck\n' + \
                      'import ' + mSModuleName + '\n' + \
                      'import ' + sSModuleName + '\n\n'
                   
            # 3.2 QC properties
            propertySource = propertySource.replace(DEFAULT_STUDENT_MODULE_NAME, sSModuleName)
            propertySource = propertySource.replace(DEFAULT_MODEL_MODULE_NAME, mSModuleName)

            wSource += propertySource + '\n\n'
            # main function
            wSource += 'main = quickCheck ' + propertyName

            self._writeFile(wSource, wFileName)
        
            # TODO: 
            # 4. copy files to jail using ssh
            #executeOsCmd(sCommandCopy % (mSFilename + '.hs'))
            #executeOsCmd(sCommandCopy % (sSFilename + '.hs'))
            #executeOsCmd(sCommandCopy % (wFilename + '.hs'))
        
            # 5. exceute wrapper file
            stdout, stdin, stderr = os.popen3('runhugs %s' % (wFileName,))
            resultin = stdin.read()
            resulterr = stderr.read()

            # set result as feedback
            if resulterr != '':
                m = re.findall('.hs":(\d+)', resulterr)
                resulterr = re.sub('.hs":(\d+)', '.hs":%s' % (int(m[0])-2), resulterr)

                self.setAuto_feedback(resulterr)
            else:
                failed = re.findall(REGEX_FAILED, resultin)
                passed = re.findall(REGEX_PASSED, resultin)
                
                if len(failed) != 0:
                    result = self.translate(\
                        msgid   = 'msg_falsifiable',\
                        domain  = I18N_DOMAIN,\
                        default = 'Your submission failed. Test case was: %s (%s)' % \
                            (failed[0][1], propertyName))

                elif len(passed) != 0:
                    result = self.translate(\
                        msgid   = 'msg_passed',\
                        domain  = I18N_DOMAIN,\
                        default = 'Your submission passed all %s tests. (%s)' % \
                            (passed[0], propertyName))
                    
                    solvedProperties.append(propertyName)

                else:
                    result = ''

                self.setAuto_feedback(self.getAuto_feedback() + '\n' + result)

            os.remove(wFileName)

        # set solved
        self.setSolved((len(solvedProperties) == len(propertyNames)))
        
        # set state to pending
        #wtool = self.portal_workflow
        #wtool.doActionFor(self, 'review')

        # 6. delete files on jail
        os.remove(mSFileName)
        os.remove(sSFileName)

# TODO: 
#        except Exception, e:
#            return self.translate(\
#                    msgid   = 'evaluation_failed',\
#                    domain  = '',\
#                    default = 'Internal error: ' + str(e))
    
    def _getUniqueModuleName(self, prefix=''):
        """ 
        Generates a unique identifier. The prefix can be set or left blank.

        @param prefix The identifier's prefix (e.g. Student for student's Haskell module).
        @return A unique identifier with or without a prefix
        """
        return prefix + uuid()
        
    def _getTempFileName(self, moduleName, suffix='.hs'):
        """ 
        Generates a absolute path string including the path to main temp dir, 
        the name of the Haskel module and a suffix.

        @param moduleName The content of this file.
        @param suffix The file's suffix (e.g. extension). Default is .hs
        @return A string with absolute file path
        """
        return tempfile.gettempdir() + os.path.sep + moduleName + suffix

    def _writeFile(self, content, filename):
        """ 
        Writes a file with the given absolute filename and content.

        @param content The content of this file.
        @param filename The absolut e file path.
        @return nothing
        """
        file = open(filename, 'w+')
        file.write(content)
        file.flush()
        file.close()
        

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

registerType(ECAssignmentQC)

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
