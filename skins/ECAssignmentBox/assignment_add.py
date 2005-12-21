## Script (Python) "assignment_add"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=source='', file='', memberId='', msg=''
##title=Create a file for an assignment submission.
##
from DateTime import DateTime
from StringIO import StringIO

# resourcestrings
I18N_DOMAIN = 'eduComponents'

REQUEST  = container.REQUEST
RESPONSE = REQUEST.RESPONSE

# set default target action (e.g. in case of an error)
target_action = context.getTypeInfo().getActionById('view')

# was the user logged in?
if memberId == '':
    msg = context.translate(\
        msgid   = 'not_logged_in',\
        domain  = I18N_DOMAIN,\
        default = 'You need to be logged in with your user name and password.')

# has the assignmentbox expired
elif context.hasExpired():
    msg = context.translate(\
        msgid   = 'submission_rejected',\
        domain  = I18N_DOMAIN,\
        default = 'The submission period has expired. Your submission was rejected.')

# are there already submissions which cannot be superseded?
elif not context.canResubmit():
    msg = context.translate(
        msgid   = 'submission_cannot_supersede',
        domain  = I18N_DOMAIN,
        default = 'Your submission was rejected: '
        'An earlier submission is under review or has already been accepted.')

# try to read file
if msg == '':
    try:
        sstr = file.filename.read()
    except:
        sstr = file.read()

    if ((not sstr) or ((not same_type(sstr, '')) and (not same_type(sstr, u'')))):
        # The file could not be read.

        # check source and put source in an file object
        if len(source) != 0:
            file = StringIO(source)
        else:
            msg = context.translate(\
              msgid   = 'file_read_error',\
              domain  = I18N_DOMAIN,\
              default = 'No text inserted and uploaded file could not be read.')

# no erros until now, process the submission
if msg == '':
    # get current date
    now = DateTime()
    # generate a unique Id for the file
    id = str(memberId) + '.' + now.strftime('%Y%m%d') + '.' + now.strftime('%H%M%S')

    # create the assignment object
    context.invokeFactory(context.allowed_content_types[0], id)
    qca = getattr(context, id)

    qca.setField('file', file)

    filename = qca.getFilename(key='file')
    if filename:
        filename = id + '_' + filename
    else:
        # TOOD: get MIME-type and add extension
        filename = id

    qca.setFilename(filename, key='file')
    
    # The submission was sucessfully saved as assignment object.
    msg = context.translate(\
        msgid   = 'submission_success',\
        domain  = I18N_DOMAIN,\
        default = 'Your submission has been saved.')

    target_action = '%s/%s' % (qca.getId(), qca.getTypeInfo().getActionById('view'))

RESPONSE.redirect('%s/%s?portal_status_message=%s' % ( \
    context.absolute_url(), target_action, msg,))
