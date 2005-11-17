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

EC_ASSIGNMENT_BOX_META_TYPE = 'ECAssignmentBox'
EC_ASSIGNMENT_BOX_QC_META_TYPE = 'ECAssignmentBoxQC'

REQUEST  = container.REQUEST
RESPONSE = REQUEST.RESPONSE

# set default target action (e.g. in case of an error)
target_action = context.getTypeInfo().getActionById('view')

# remember the context type
contextType = context.meta_type

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
    else:
       # put file's content into source only for submissions 
       # to ECAssignmentBoxQC-objects
       if contextType == EC_ASSIGNMENT_BOX_QC_META_TYPE:
          source = sstr

# no erros until now, process the submission
if msg == '':
    # get current date
    now = DateTime()
    # generate a unique Id for the file
    id = str(memberId) + '.' + now.strftime('%Y%m%d') + '.' + now.strftime('%H%M%S')

    # create the assignment object
    context.invokeFactory(id=id, type_name=context.allowed_content_types[0])
    qca = getattr(context, id)

    qca.setField('source', source)
    #qca.setField('user_id', memberId)
    qca.setField('datetime', now)
    qca.setField('file', file)

    filename = qca.getFilename(key='file')
    if filename:
        filename = id + '_' + filename
    else:
        # TOOD: get MIME-type and add extension
        filename = id

    qca.setFilename(filename , key='file')
    
    qca.editMetadata(title=id)
    qca.editMetadata(language='') # '' means "language-neutral"

    # evaluate only in case of ECAssignmentQC
    if contextType == EC_ASSIGNMENT_BOX_QC_META_TYPE:
        result = qca.evaluate(
            context.getModel_solution(), 
            context.getQc_property(),
            context.getSpoolerConnection(),
            context.getCheckerBackend())
        
        # set next workflow state automatic
        # FIXME: This doesn't work
        #wtool = context.portal_workflow
        #wtool.doActionFor(qca, 'review')

    else:
        result = None

    if not result:
        # The submission was evaluated.
        msg = context.translate(\
            msgid   = 'submission_success_evaluation_success',\
            domain  = I18N_DOMAIN,\
            default = 'Your submission has been saved.')
    else:
        msg = result
        # The submission couldn't be evaluated.
        #msg = context.translate(\
        #    msgid   = 'submission_success_evaluation_failed',\
        #    domain  = I18N_DOMAIN,\
        #    default = 'Your solution has been submitted but could not be evaluated.')
            
        # TODO: send email to teacher

    target_action = '%s/%s' % (qca.getId(), qca.getTypeInfo().getActionById('view'))

RESPONSE.redirect('%s/%s?portal_status_message=%s' % ( \
    context.absolute_url(), target_action, msg,))
