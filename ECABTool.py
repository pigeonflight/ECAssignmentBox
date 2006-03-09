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

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
#from OFS.SimpleItem import SimpleItem
from OFS.Folder import Folder
from Products.CMFCore.utils import UniqueObject, getToolByName

from Products.Archetypes.atapi import *
from Products.DCWorkflow.Transitions import TRIGGER_USER_ACTION

from urlparse import urlsplit, urlunsplit
from socket import gethostname, getfqdn
from string import split, join

# local imports
from Products.ECAssignmentBox.Statistics import Statistics
from Products.ECAssignmentBox.config import I18N_DOMAIN, ECA_WORKFLOW_ID

class ECABTool(UniqueObject, Folder):
    """Various utility methods."""

    id = 'ecab_utils'
    portal_type = meta_type = 'ECAssignmentBox Utility Tool'
    
    security = ClassSecurityInfo()

    student_id_attr = ''
    major_attr = ''

    # manage options
    manage_options = (
        (Folder.manage_options[0],)
        + Folder.manage_options[2:]
        )

    # set properties
    _properties = Folder._properties + (
        {'id':'student_id_attr',
         'type':'ustring',
         'mode':'w',
        },
        {'id':'major_attr',
         'type':'ustring',
         'mode':'w',
        },
    )

    # -- constructor -----------------------------------------------------------
    def __init__(self):
        """
        """
        pass


    # -- methods ---------------------------------------------------------------
    security.declarePublic('localizeNumber')
    def localizeNumber(self, format, number):
        """A simple method for localized formatting of decimal
        numbers.  Theoretically, one could use locale.format(), but it
        isn't portable enough."""
        if type(number) not in (int, long, float):
            return number
        
        decimalSeparator = self.translate(msgid = 'decimal_separator',
                                          domain = I18N_DOMAIN,
                                          default = '.')
        retval = format % number
        return retval.replace('.', decimalSeparator)

    
    security.declarePublic('getFullNameById')
    def getFullNameById(self, id):
        """
        """
        mtool = self.portal_membership
        member = mtool.getMemberById(id)
        
        if not member:
            return id
        
        try:
            sn        = member.getProperty('sn')
            givenName = member.getProperty('givenName')
        except:
            fullname = member.getProperty('fullname', '')
            
            if fullname == '':
                return id
            
            if fullname.find(' ') == -1:
                return fullname
            
            sn = fullname[fullname.rfind(' ') + 1:]
            givenName = fullname[0:fullname.find(' ')]
            
        return sn + ', ' + givenName


    security.declarePublic('getUserPropertyById')
    def getUserPropertyById(self, id, property=''):
        """
        """
        mtool = self.portal_membership
        member = mtool.getMemberById(id)
        
        try:
            value = member.getProperty(property)
        except:
            return None
        
        return value


    security.declarePublic('isAssignmentBoxType')
    def isAssignmentBoxType(self, obj):
        """
        """
        return hasattr(obj, 'getAssignmentsSummary')


    #security.declarePublic('findAssignments')
    def findAssignments(self, context, id):
        """
        """
        ct = getToolByName(self, 'portal_catalog')
        ntp = getToolByName(self, 'portal_properties').navtree_properties
        currentPath = None
        query = {}
        
        if context == self:
            currentPath = getToolByName(self, 'portal_url').getPortalPath()
            query['path'] = {'query':currentPath,
                             'depth':ntp.getProperty('sitemapDepth', 2)}
        else:
            currentPath = '/'.join(context.getPhysicalPath())
            query['path'] = {'query':currentPath, 'navtree':1}
        
        query['portal_type'] = ('ECAssignment',)
        #rawresult = ct(**query)
        rawresult = ct(path=currentPath, portal_type='ECAssignment',
                       Creator=id)
        return rawresult


    #security.declarePublic('calculateMean')
    def calculateMean(self, list):
        """
        """
        try:
            stats = Statistics(list)
        except:
            return None

        return stats.mean


    #security.declarePublic('calculateMedian')
    def calculateMedian(self, list):
        """
        """
        try:
            stats = Statistics(list)
        except:
            return None

        return stats.median


    #security.declarePrivate('getWfStates')
    def getWfStates(self, wfName=ECA_WORKFLOW_ID):
        """
        @return a list containing all state keys in assignment's workflow
        """
        wtool = self.portal_workflow
        return wtool.getWorkflowById(wfName).states.keys()


    #security.declarePrivate('getWfStatesDisplayList')
    def getWfStatesDisplayList(self, wfName=ECA_WORKFLOW_ID):
        """
        @return a DisplayList containing all state keys and state titles in 
                assignment's workflow
        """
        dl = DisplayList(())

        wtool = self.portal_workflow
        wf = wtool.getWorkflowById(wfName)
        stateKeys = self.getWfStates(wfName)
        
        for key in stateKeys:
            dl.add(key, wf.states[key].title)

        #return dl.sortedByValue()
        return dl


    #security.declarePrivate('getWfTransitionsDisplayList')
    def getWfTransitionsDisplayList(self, wfName=ECA_WORKFLOW_ID):
        """
        @return a DisplayList containing all transition keys and titles in 
                assignment's workflow
        """
        dl = DisplayList(())

        wtool = self.portal_workflow
        wf = wtool.getWorkflowById(wfName)
        transKeys = wf.transitions.keys()
        
        for key in transKeys:
            # trigger type must be TRIGGER_USER_ACTION, 
            # i.e., transition can be initiated by a user
            if wf.transitions[key].trigger_type == TRIGGER_USER_ACTION:
                dl.add(key, wf.transitions[key].actbox_name)

        return dl.sortedByValue()
        #return dl


    def normalizeURL(self, url):
        """
        Takes a URL (as returned by absolute_url(), for example) and
        replaces the hostname with the actual, fully-qualified
        hostname.
        """
        url_parts = urlsplit(url)
        hostpart  = url_parts[1]

        (hostname, port) = split(hostpart, ':')

        if hostname == 'localhost' or hostname == '127.0.0.1':
            hostname = getfqdn(gethostname())
        else:
            hostname = getfqdn(hostname)

        hostpart = join((hostname, port), ':')
        url = urlunsplit((url_parts[0], hostpart, \
                          url_parts[2], url_parts[3], url_parts[4]))
        return url


InitializeClass(ECABTool)
