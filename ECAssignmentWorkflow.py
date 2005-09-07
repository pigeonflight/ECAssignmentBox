# -*- coding: utf-8 -*-
# $Id$
#
# Copyright (c) 2005 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECAssignmentBox.

"""
Simple Publication Workflow (ECAssignmentBox)
"""

__author__    = '''ma <amelung@iws.cs.uni-magdeburg.de>'''
__docformat__ = 'plaintext'
__version__   = '$Revision$'

from Products.CMFCore.WorkflowTool import addWorkflowFactory
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition

def setupAssignment_workflow(wf):
    """Assignment Workflow definition"""

    wf.setProperties(title='Assignment workflow [EC]')
    for s in ['marked', 
              'pending', 
              'submitted']:
        wf.states.addState(s)

    for t in ['review',
              'mark',
              'retract']:
        wf.transitions.addTransition(t)

    for v in ['review_history',
              'comments',
              'time',
              'actor',
              'action']:
        wf.variables.addVariable(v)

    for p in ('Access contents information',
              'Modify portal content',
              'View',
              'List folder contents'):
        wf.addManagedPermission(p)

    wf.states.setInitialState('submitted')

    sdef = wf.states['submitted']
    sdef.setProperties(title="""Submitted""",
                       transitions=('review',))
    sdef.setPermission('Access contents information',
                       0,
                       ['Owner',
                        'Reviewer',
                        'Manager'])
    sdef.setPermission('Modify portal content',
                       0,
                       ['Manager',
                        'Reviewer'])
    sdef.setPermission('View',
                       0,
                       ['Owner',
                        'Reviewer',
                        'Manager'])
    sdef.setPermission('List folder contents',
                       0,
                       ['Reviewer',
                        'Manager'])

    sdef = wf.states['pending']
    sdef.setProperties(title="""Pending""",
                       transitions=('mark',))
    sdef.setPermission('Access contents information',
                       0,
                       ['Manager',
                        'Reviewer'
                        'Owner'])
    sdef.setPermission('Modify portal content',
                       0,
                       ['Manager'])
    sdef.setPermission('View',
                       0,
                       ['Manager',
                        'Reviewer',
                        'Owner'])
    sdef.setPermission('List folder contents',
                       0,
                       ['Reviewer',
                        'Manager'])

    sdef = wf.states['marked']
    sdef.setProperties(title="""Marked""",
                       transitions=('retract',))
    sdef.setPermission('Access contents information',
                       0,
                       ['Manager',
                        'Reviewer'
                        'Owner'])
    sdef.setPermission('Modify portal content',
                       0,
                       ['Manager'])
    sdef.setPermission('View',
                       0,
                       ['Manager',
                        'Reviewer',
                        'Owner'])
    sdef.setPermission('List folder contents',
                       0,
                       ['Reviewer',
                        'Manager'])

    tdef = wf.transitions['review']
    tdef.setProperties(title="""Assignment is locked and can not be deleted by the submitter""",
                       new_state_id="""pending""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""Review""",
                       actbox_url="""""",
                       actbox_category="""workflow""",
                       props={'guard_permissions': 'Review portal content'},
                       )

    tdef = wf.transitions['mark']
    tdef.setProperties(title="""Reviewer releases marks for assignment""",
                       new_state_id="""marked""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""Mark""",
                       actbox_url="""""",
                       actbox_category="""workflow""",
                       props={'guard_permissions': 'Review portal content'},
                       )

    tdef = wf.transitions['retract']
    tdef.setProperties(title="""Reviewer makes marks private""",
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
                   id='ec_assignment_workflow',
                   title='Assignment workflow [EC]')
