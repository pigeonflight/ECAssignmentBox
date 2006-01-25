# -*- coding: utf-8 -*-
# $Id$
#
# Copyright (c) 2005 Otto-von-Guericke-Universität Magdeburg
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

from StringIO import StringIO

from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.Archetypes.public import listTypes
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.migrate import migrateFTIs

# ECAssignmentBox
from Products.ECAssignmentBox.config import *

def install(self):
    out = StringIO()

    installTypes(self, out, listTypes(PROJECTNAME), PROJECTNAME)
    migrateFTIs(self, product=PROJECTNAME)
    install_subskin(self, out, GLOBALS)

    # install assignment workflow
    install_workflow(self, out)
    
    print >> out, "Successfully installed %s." % PROJECTNAME

    # continue with my custom tool
    if hasattr(self, 'ecab_utils'):
        self.manage_delObjects(['ecab_utils'])
        out.write('Deleting old ecab_utils; make sure you repeat customizations.\n')
    addTool = self.manage_addProduct[PROJECTNAME].manage_addTool
    addTool(TOOL_META)
    # set title of tool:
    tool = getToolByName(self, TOOL_NAME)
    tool.title = TOOL_TITLE
    print >> out, "Added ecab_utils to the portal root folder.\n"

    return out.getvalue()

def install_workflow(self, out):
    wf_tool = getToolByName(self, 'portal_workflow')
    
    if ECA_WORKFLOW_ID in wf_tool.objectIds():
        wf_tool._delObject(ECA_WORKFLOW_ID)
    
    wf_tool.manage_addWorkflow(id = ECA_WORKFLOW_ID,
                               workflow_type = '%s (%s)' % (ECA_WORKFLOW_ID, ECA_WORKFLOW_TITLE))

    wf_tool.setChainForPortalTypes((ECA_META,), ECA_WORKFLOW_ID)
    #wf_tool.setChainForPortalTypes(('ECAssignmentQC',), ECA_WORKFLOW_ID)
    
    # in case the workflows have changed, update all workflow-aware objects
    wf_tool.updateRoleMappings()
    
    print >> out, "Successfully installed ECAssignment workflow."
