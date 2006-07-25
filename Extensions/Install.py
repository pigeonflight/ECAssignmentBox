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

def addPrefsPanel(self, out):
    """
    """
    cp = getToolByName(self, 'portal_controlpanel', None)
    if not cp:
        out.write("No control panel found. Skipping installation of the setup panel.\n")
    else:
        cp.addAction(id = TOOL_NAME,
                     name = TOOL_TITLE,
                     action = 'string:${portal_url}/ecabtool_form',
                     permission = 'Manage portal',
                     category = 'Products',
                     appId = PROJECTNAME,
                     imageUrl = TOOL_ICON,
                     description = '')

    out.write("Added '%s' to the preferences panel.\n" % TOOL_TITLE)


def removePrefsPanel(self):
    """
    """
    cp = getToolByName(self, 'portal_controlpanel', None)
    if cp:
        cp.unregisterApplication(PROJECTNAME)


def install(self):
    out = StringIO()

    installTypes(self, out, listTypes(PROJECTNAME), PROJECTNAME)
    migrateFTIs(self, product=PROJECTNAME)
    install_subskin(self, out, GLOBALS)

    # install assignment workflow
    install_workflow(self, out)
    
    print >> out, "Successfully installed %s." % PROJECTNAME

    # install site-wide properties to portal_properties
    install_properties(self, out)

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

    # register tool to preferences panel
    addPrefsPanel(self, out)

    # enable portal_factory for given types
    factory_tool = getToolByName(self, 'portal_factory')
    factory_types=[
        ECAB_META,
        ECA_META,
        ] + factory_tool.getFactoryTypes().keys()
    factory_tool.manage_setPortalFactoryTypes(listOfTypeIds=factory_types)

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


def install_properties(self, out):
    """
    Install properties for ECAssignmentBox
    """
    if not hasattr(self.portal_properties, 'ecab_properties'):
        self.portal_properties.addPropertySheet('ecab_properties',
                                                'ECAssignmentBox properties')
    
    props = self.portal_properties.ecab_properties

    if not hasattr(props, 'student_id_attr'):
        props._setProperty('student_id_attr', "", 'string')
        
    if not hasattr(props, 'major_attr'):
        props._setProperty('major_attr', "", 'string')

    if not hasattr(props, 'personal_title_attr'):
        props._setProperty('personal_title_attr', "", 'string')

    out.write("Installed site-wide ECAssignmentBox properties.\n")


def uninstall(self, reinstall):
    """ 
    Uninstalls the product.
    """
    out = StringIO()

    removePrefsPanel(self)

    # FIXME: use method
    if hasattr(self, TOOL_NAME):
        self.manage_delObjects([TOOL_NAME])
        out.write('Removed %s.\n' % TOOL_NAME)

    # Remove property sheet
    if not reinstall:
        if hasattr(self.portal_properties, 'ecab_properties'):
            self.portal_properties.manage_delObjects('ecab_properties')

    print >> out, "Successfully uninstalled %s." % PROJECTNAME
    return out.getvalue()
