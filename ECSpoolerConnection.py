# -*- coding: utf-8 -*-
# $Id$
#
# Copyright (c) 2005 Otto-von-Guericke-University, Magdeburg
#
# This file is part of ECAssignmentBox.
"""
This content type provides information about the ECSpooler which is used for
automatic students' program evaluation
"""
import xmlrpclib

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.atapi import *
from Products.CMFCore import CMFCorePermissions

from Products.ECAssignmentBox.config import I18N_DOMAIN

localSchema = BaseSchema + Schema((
    StringField(
        'host',
        required=True,
        widget = StringWidget(
            modes=('edit'),
            label = "Host",
            label_msgid = "label_host",
            description = "Enter name of the host (e.g. lls.cs.uni-magdeburg.de).",
            description_msgid = "help_host",
            i18n_domain = I18N_DOMAIN,
        ),
    ),

    IntegerField(
        'port',
        required=True,
        widget = IntegerWidget(
            modes=('edit'),
            label = "Port",
            label_msgid = "label_port",
            description = "Enter port number (e.g. 8000).",
            description_msgid = "help_host",
            i18n_domain = I18N_DOMAIN,
        ),
    ),

    StringField(
        'username',
        required=True,
        #populate=False,
        widget = StringWidget(
            modes=('edit'),
            label = "Username",
            label_msgid = "label_username",
            description = "Enter username for this connection (e.g. demo).",
            description_msgid = "help_username",
            i18n_domain = I18N_DOMAIN,
        ),
    ),

    StringField(
        'password',
        required=True,
        #populate=False,
        widget = PasswordWidget(
            label = "Password",
            label_msgid = "label_password",
            description = "Enter password for this connection.",
            description_msgid = "help_password",
            i18n_domain = I18N_DOMAIN,
        ),
    ),

))

class ECSpoolerConnection(BaseContent):
    """
    ...
    """

    security = ClassSecurityInfo()

    __implements__ = (BaseFolder.__implements__, OrderedBaseFolder.__implements__, )

    _at_rename_after_creation = True

    schema = localSchema
    meta_type = "ECSpoolerConnection"
    archetype_name = "SpoolerConnection"
    content_icon = "control-16.jpg"            

    security.declarePublic('testConnection')
    def testConnection(self):
        AUTH  = {'username':self.username, 'password':self.password}

        try:
            handle = xmlrpclib.Server("http://%s:%d" % (self.host, self.port))
            status = handle.getStatus(AUTH)

            if type(status) == list:
                return status[1]
            elif type(status) == dict:
                return self.translate(\
                            msgid   = 'test_succeeded',\
                            domain  = I18N_DOMAIN,\
                            default = 'Connection tested successfully. The ' + \
                                      'following checker backends are available: %s' \
                                      % ', '.join(status['checkers'])
                            )
            else:
                return self.translate(\
                            msgid   = 'test_pending',\
                            domain  = I18N_DOMAIN,\
                            default = 'Unknown result from server: %s' % repr(status)
                            )

        except Exception, e:
            return self.translate(\
                    msgid   = 'test_failed',\
                    domain  = I18N_DOMAIN,\
                    default = 'Could not connect to spooler server. %s' % e)
    
    actions =  (
        {
        'action':      "string:$object_url/spooler_test",
        'category':    "object",
        'id':          'test',
        'name':        'Test',
        'permissions': ("Edit",),
        'condition'  : 'python:1'
        },

#        {
#        'action':      "string:$object_url/spooler_edit",
#        'category':    "object",
#        'id':          'edit',
#        'name':        'edit',
#        'permissions': ("View",),
#        'condition'  : 'python:1'
#        },
    )

registerType(ECSpoolerConnection)
