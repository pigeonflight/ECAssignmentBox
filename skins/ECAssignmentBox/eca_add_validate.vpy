## Script (Python) "submission_validate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##
REQUEST = context.REQUEST

# resourcestrings
I18N_DOMAIN = 'eduComponents'
failure_msg = None

user_id = REQUEST.get('user_id', None)

# was the user logged in?
if (not user_id) or (user_id == ''):
    failure_msg = context.translate(\
            msgid   = 'not_logged_in',\
            domain  = I18N_DOMAIN,\
            default = 'You need to be logged in with your username and password.')

# has the assignmentbox expired
elif context.hasExpired():
    failure_msg = context.translate(\
        msgid   = 'submission_rejected',\
        domain  = I18N_DOMAIN,\
        default = 'The submission period has expired. Your submission was rejected.')

# are there already submissions which cannot be superseded?
elif not context.canResubmit():
    failure_msg = context.translate(
        msgid   = 'submission_cannot_supersede',
        domain  = I18N_DOMAIN,
        default = 'Your submission was rejected: ' +
                  'An earlier submission is under review or has already been accepted.')


if failure_msg:
    return state.set(status = 'failure', portal_status_message = failure_msg)
else:
    return state
