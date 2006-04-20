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

"""
Assignment Workflow
"""

__author__    = 'ma <amelung@iws.cs.uni-magdeburg.de>'
__docformat__ = 'plaintext'
__version__   = '$Revision$'

from Products.CMFCore.WorkflowTool import addWorkflowFactory
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.DCWorkflow.Transitions import TRIGGER_AUTOMATIC, TRIGGER_USER_ACTION, TRIGGER_WORKFLOW_METHOD

from Products.CMFCore.permissions import ManageProperties

from Products.ECAssignmentBox.config import *

def setupAssignment_workflow(wf):
    """Assignment Workflow definition"""

    wf.setProperties(title='Assignment workflow [EC]')
    for s in ['graded',
              'accepted', 'rejected', 'superseded',
              'pending', 
              'submitted']:
        wf.states.addState(s)

    for t in ['review',
              'accept', 'reject', 'supersede',
              'grade',
              'retract']:
        wf.transitions.addTransition(t)

    for v in ['review_history',
              'comments',
              'time',
              'actor',
              'action']:
        wf.variables.addVariable(v)

    for p in ('Access contents information',
              ManageProperties,
              'Modify portal content',
              'View',
              'List folder contents'):
        wf.addManagedPermission(p)

    wf.states.setInitialState('submitted')

    sdef = wf.states['submitted']
    sdef.setProperties(title="""Submitted""",
                       transitions=('review', 'accept', 'reject', 'supersede'))
    sdef.setPermission('Access contents information',
                       0,
                       ['Owner',
                        'Reviewer',
                        'Manager',
                        'ECAssignment Grader'])
    sdef.setPermission('Modify portal content',
                       0,
                       [#'Owner',
                        'Reviewer',
                        'Manager',
                        'ECAssignment Grader'])
    sdef.setPermission(ManageProperties,
                       0,
                       [#'Owner',
                        'Reviewer',
                        'Manager',
                        'ECAssignment Grader'])
    sdef.setPermission('View',
                       0,
                       ['Owner',
                        'Reviewer',
                        'Manager',
                        'ECAssignment Grader'])
    sdef.setPermission('List folder contents',
                       0,
                       ['Reviewer',
                        'Manager',
                        'ECAssignment Grader'])

    sdef = wf.states['pending']
    sdef.setProperties(title="""Pending""",
                       transitions=('accept', 'reject', 'grade', 'retract'))
    sdef.setPermission('Access contents information',
                       0,
                       ['Owner',
                        'Reviewer'
                        'Manager',
                        'ECAssignment Grader'])
    sdef.setPermission('Modify portal content',
                       0,
                       ['Reviewer',
                        'Manager',
                        'ECAssignment Grader'])
    sdef.setPermission(ManageProperties,
                       0,
                       [#'Owner',
                        'Reviewer',
                        'Manager',
                        'ECAssignment Grader'])
    sdef.setPermission('View',
                       0,
                       ['Owner',
                        'Reviewer',
                        'Manager',
                        'ECAssignment Grader'])
    sdef.setPermission('List folder contents',
                       0,
                       ['Reviewer',
                        'Manager',
                        'ECAssignment Grader'])

    sdef = wf.states['graded']
    sdef.setProperties(title="""Graded""",
                       transitions=('retract',))
    sdef.setPermission('Access contents information',
                       0,
                       ['Owner',
                        'Reviewer',
                        'Manager'])
    sdef.setPermission('Modify portal content',
                       0,
                       ['Reviewer',
                        'Manager'])
    sdef.setPermission('View',
                       0,
                       ['Owner',
                        'Reviewer',
                        'Manager',
                        'ECAssignment Viewer'])
    sdef.setPermission('List folder contents',
                       0,
                       ['Reviewer',
                        'Manager'])

    sdef = wf.states['accepted']
    sdef.setProperties(title="""Accepted""",
                       transitions=('retract', 'grade'))
    sdef.setPermission('Access contents information',
                       0,
                       ['Owner',
                        'Reviewer',
                        'Manager'])
    sdef.setPermission('Modify portal content',
                       0,
                       ['Reviewer',
                        'Manager'])
    sdef.setPermission('View',
                       0,
                       ['Owner',
                        'Reviewer',
                        'Manager',
                        'ECAssignment Viewer'])
    sdef.setPermission('List folder contents',
                       0,
                       ['Reviewer',
                        'Manager'])

    sdef = wf.states['superseded']
    sdef.setProperties(title="""Superseded""",
                       transitions=('retract',))
    sdef.setPermission('Access contents information',
                       0,
                       [#'Owner',
                        'Reviewer',
                        'Manager'])
    sdef.setPermission('Modify portal content',
                       0,
                       ['Reviewer',
                        'Manager'])
    sdef.setPermission(ManageProperties,
                       0,
                       [#'Owner',
                        'Reviewer',
                        'Manager'
                        ])
    sdef.setPermission('View',
                       0,
                       ['Owner',
                        'Reviewer',
                        'Manager'])
    sdef.setPermission('List folder contents',
                       0,
                       ['Reviewer',
                        'Manager'])

    sdef = wf.states['rejected']
    sdef.setProperties(title="""Rejected""",
                       transitions=('retract',))
    sdef.setPermission('Access contents information',
                       0,
                       ['Owner',
                        'Reviewer',
                        'Manager'])
    sdef.setPermission('Modify portal content',
                       0,
                       ['Reviewer',
                        'Manager'])
    sdef.setPermission('View',
                       0,
                       ['Owner',
                        'Reviewer',
                        'Manager',
                        'ECAssignment Viewer'])
    sdef.setPermission('List folder contents',
                       0,
                       ['Reviewer',
                        'Manager'])

    tdef = wf.transitions['review']
    tdef.setProperties(title="""Assignment is locked and cannot be deleted by the submitter""",
                       new_state_id="""pending""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""Review""",
                       actbox_url="""""",
                       actbox_category="""workflow""",
                       props={'guard_permissions': 'Review portal content'},
                       )

    tdef = wf.transitions['accept']
    tdef.setProperties(title="""Reviewer accepts the assignment""",
                       new_state_id="""accepted""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""Accept""",
                       actbox_url="""""",
                       actbox_category="""workflow""",
                       props={'guard_permissions': 'Review portal content'},
                       )

    tdef = wf.transitions['reject']
    tdef.setProperties(title="""Reviewer rejects the assignment""",
                       new_state_id="""rejected""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""Reject""",
                       actbox_url="""""",
                       actbox_category="""workflow""",
                       props={'guard_permissions': 'Review portal content'},
                       )

    tdef = wf.transitions['supersede']
    tdef.setProperties(title="""Replace assignment with a newer submission""",
                       new_state_id="""superseded""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""Supersede""",
                       actbox_url="""""",
                       actbox_category="""workflow""",
                       props={'guard_roles': 'Owner'},
                       )

    tdef = wf.transitions['grade']
    tdef.setProperties(title="""Reviewer grades the assignment""",
                       new_state_id="""graded""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""Grade""",
                       actbox_url="""""",
                       actbox_category="""workflow""",
                       props={'guard_permissions': 'Review portal content'},
                       )

    tdef = wf.transitions['retract']
    tdef.setProperties(title="""Assignment is reset to initial state""",
                       new_state_id="""submitted""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""Retract""",
                       actbox_url="""""",
                       actbox_category="""workflow""",
                       props={'guard_permissions': 'Review portal content'},
                       )

    wf.variables.setStateVar('review_state')

    vdef = wf.variables['review_history']
    vdef.setProperties(description="""Provides access to workflow history""",
                       default_value="""""",
                       default_expr="""state_change/getHistory""",
                       for_catalog=0,
                       for_status=0,
                       update_always=0,
                       props={'guard_permissions': 'Request review; Review portal content'})
    vdef = wf.variables['comments']
    vdef.setProperties(description="""Comments about the last transition""",
                       default_value="""""",
                       default_expr="""python:state_change.kwargs.get('comment', '')""",
                       for_catalog=0,
                       for_status=1,
                       update_always=1,
                       props=None)
    vdef = wf.variables['time']
    vdef.setProperties(description="""Time of the last transition""",
                       default_value="""""",
                       default_expr="""state_change/getDateTime""",
                       for_catalog=0,
                       for_status=1,
                       update_always=1,
                       props=None)
    vdef = wf.variables['actor']
    vdef.setProperties(description="""The ID of the user who performed the last transition""",
                       default_value="""""",
                       default_expr="""user/getUserName""",
                       for_catalog=0,
                       for_status=1,
                       update_always=1,
                       props=None)
    vdef = wf.variables['action']
    vdef.setProperties(description="""The last transition""",
                       default_value="""""",
                       default_expr="""transition/getId|nothing""",
                       for_catalog=0,
                       for_status=1,
                       update_always=1,
                       props=None)

def createAssignment_workflow(id):
    """workflow creation"""
    ob = DCWorkflowDefinition(id)
    setupAssignment_workflow(ob)
    return ob

addWorkflowFactory(createAssignment_workflow,
                   id = ECA_WORKFLOW_ID,
                   title= ECA_WORKFLOW_TITLE)
