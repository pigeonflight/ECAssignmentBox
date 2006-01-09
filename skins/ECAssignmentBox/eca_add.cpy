## Script (Python) "assignment_add"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=answer='', file='', user_id='', msg=''
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

# remember the context type
contextType = context.meta_type

if not file:
    # no file uploaded, lets try to read the text field (answer)
    if len(answer) != 0:
        file = StringIO(answer)
    else:
        # neither file nor answer available
        msg = context.translate(\
          msgid   = 'file_read_error',
          domain  = I18N_DOMAIN,
          default = 'Neither answer nor uploaded file found.')

        return state.set(status = 'failure', portal_status_message = msg)

# get current date and time
now = DateTime()
# generate unique Id for this submission
id = str(user_id) + '.' + now.strftime('%Y%m%d') + '.' + now.strftime('%H%M%S')
    
# create assignment object
context.invokeFactory(id=id, type_name=context.allowed_content_types[0])
qca = getattr(context, id)

# set file
qca.setFile(file)

# modify filename
filename = qca.getFilename(key='file')
if filename:
    filename = id + '_' + filename
else:
    # TOOD: get MIME-type and add extension
    filename = id
    
qca.setFilename(filename, key='file')
    
# evaluate this submission
result = qca.evaluate(context)
#context.getModelSolution(), 
#context.getComparator(),
#context.getBackend(),
#context.getTestData(),
            
if not result:
    # The submission was evaluated.
    msg = context.translate(
        msgid   = 'submission_success_evaluation_success',
        domain  = I18N_DOMAIN,
        default = 'Your submission has been saved.')
else:
    msg = result
    
target_action = '%s/%s' % (qca.getId(), qca.getTypeInfo().getActionById('view'))

#return state.set(portal_status_message = msg)
RESPONSE.redirect('%s/%s?portal_status_message=%s' % 
            (context.absolute_url(), target_action, msg,))

