# -*- coding: utf-8 -*-
# $Id$
#
# Copyright (c) 2005 Otto-von-Guericke-University, Magdeburg
#
# This file is part of ECAssignmentBox.
"""
TODO: 
- use ECSpooler for program evaluation
- check spooler server in view or edit mode for results, if auto_feedback is
  not set with a value
- implement ECSpoolerConnection type for Plone site
- separate syntax and sematic erros
- if after MAX_WAIT_TIME we got no result from spooler, we must retry 
  pollResult wirh jobId every time view or edit actions are called by
  a user
  
"""

import os
import re
import tempfile
import sys
import xmlrpclib

from time import *

from urllib import quote

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.CMFCore import CMFCorePermissions

from Products.ECAssignmentBox.config import I18N_DOMAIN
from Products.ECAssignmentBox.ECAssignment import ECAssignment

# resourcestring
REGEX_FAILED = '(?m)Falsifiable, after \d+ tests?:'
REGEX_FAILED_TESTDATA = '\n(-?.+)'
REGEX_PASSED_TESTNUMBER = 'passed (\d+)'
REGEX_LINENUMBER = ':\d+'
DEFAULT_MODEL_MODULE_NAME = '#Model#'
DEFAULT_STUDENT_MODULE_NAME =  '#Student#'

# set max wait time to 15 sec
MAX_WAIT_TIME = 15

# get log
from Log import *
log = MyLog(LOG_DEBUG)

# define schema
localSchema = Schema((
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
))


class ECAssignmentQC(ECAssignment):
    """
    The ECAssignmentQC class, inherited from ECAssignment and enhanced
    with the auto_feedback field
    """
    security = ClassSecurityInfo()

    schema = ECAssignment.schema + localSchema
    meta_type = "ECAssignmentQC"
    archetype_name = "Assignment (Haskell QuickCheck)"
    content_icon = "sheet-16.png" 

    security.declarePublic('evaluate')
    def evaluate(self, modelSource, propertySource, spooler, checker):
        """
        Evaluates the student solution via ECSpooler
        """
        if (self.getSource() == None) or (modelSource == None) or \
           (propertySource == None):
            return self.translate(\
                        msgid   = 'evaluation_failed',\
                        domain  = I18N_DOMAIN,\
                        default = 'Some values are not set properly.')

        wtool = self.portal_workflow
        wf = wtool.getWorkflowsFor(self)[0]
        if wf.isActionSupported(self, 'review'):
            wtool.doActionFor(self, 'review', comment='queued for automatic checking by %s' % checker)

        # set connection properties
        AUTH = {'username':spooler.username, 'password':spooler.password}
        HOST = spooler.host
        PORT = spooler.port
        
        # get an xmlrpc handle
        handle = xmlrpclib.Server("http://%s:%d" % (HOST, PORT))

        # enqueue students' solution
        # FIXME: rename sample_soution to model_solution
        enq = handle.enqueue(AUTH, {
            #"checker"         : "haskell_qc",
            "checker"         : checker,
            "student_solution": self.getSource(),
            "sample_solution" : modelSource,
            "comparator"      : propertySource,
        })

        log.debug('[%s] Enqueue: %s' % (self.getId(), repr(enq)))

        # remember job id and set inital values for result and iterator
        id = enq[1]
        result = {}
        i = 0
    
        # wait until a result has polled or max time has gone
        while (not result.has_key(id)) and (i < MAX_WAIT_TIME):
            sleep(1)
            result = handle.pollResult(AUTH, id)
            log.debug('[%s] PollResult: %s' % (self.getId(), repr(result)))
            i += 1

        if result.has_key(id):
            self.setAuto_feedback(result[id][1])
            #self.setSolved(result[id][0])
    
            if wf.isActionSupported(self, 'retract'):
                wtool.doActionFor(self, 'retract', comment='automatically checked by %s' % checker)

        else:
            log.debug('[%s] no result after %d sec' % (self.getId(), MAX_WAIT_TIME))

    # define actions
    actions = (
        {
        'action':      "string:$object_url/assignment_view",
        'category':    "object",
        'id':          'view',
        'name':        'View',
        'permissions': ("View",),
        'condition'  : 'python:1'
        },
        {
        'action':      "string:$object_url/assignment_edit",
        'category':    "object",
        'id':          'edit',
        'name':        'Edit',
        'permissions': ("Edit",),
        'condition'  : 'python:1'
        },
    )

registerType(ECAssignmentQC)