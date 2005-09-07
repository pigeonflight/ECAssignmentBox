# -*- coding: utf-8 -*-
# $Id$
#
# Copyright (c) 2005 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECAssignmentBox.

from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.Archetypes.public import listTypes
from Products.CMFCore.utils import getToolByName
from Products.ECAssignmentBox.config import *
from StringIO import StringIO


def install(self):
    out = StringIO()

    installTypes(self, out, listTypes(PROJECTNAME), PROJECTNAME)

    install_subskin(self, out, GLOBALS)

    # install assignment workflow
    install_workflow(self, out)
    
    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()


def install_workflow(self, out):
    wf_tool = getToolByName(self, 'portal_workflow')
    
    if 'ec_assignment_workflow' in wf_tool.objectIds():
        wf_tool._delObject('ec_assignment_workflow')
    
    wf_tool.manage_addWorkflow(id = 'ec_assignment_workflow',
                               workflow_type = 'ec_assignment_workflow (Assignment workflow [EC])')

    wf_tool.setChainForPortalTypes(('ECAssignment',), 'ec_assignment_workflow')
    wf_tool.setChainForPortalTypes(('ECAssignmentQC',), 'ec_assignment_workflow')
    
    # in case the workflows have changed, update all workflow-aware objects
    wf_tool.updateRoleMappings()
    
    print >> out, "Successfully installed ECAssignment workflow."