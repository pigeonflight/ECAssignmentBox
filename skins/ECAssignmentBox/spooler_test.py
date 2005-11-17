## Script (Python) "assignment_add"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Test connection to spooler server
##

# resourcestrings
I18N_DOMAIN = 'eduComponents'

REQUEST  = container.REQUEST
RESPONSE = REQUEST.RESPONSE

# set default target action
target_action = context.getTypeInfo().getActionById('view')

# call test method in ECSpoolerConnection instance
msg = context.testConnection()

RESPONSE.redirect('%s/%s?portal_status_message=%s' % \
    (context.absolute_url(), target_action, msg,)
)
