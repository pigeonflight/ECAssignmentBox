## Script (Python) "downloadAnswerTemplate"
##parameters=
##title=
##

REQUEST  = context.REQUEST
RESPONSE = REQUEST.RESPONSE

ecab_utils = context.ecab_utils

exportEncoding = 'iso-8859-15'
siteEncoding   = context.getCharset()

output = context.getField('answerTemplate').getAccessor(context)()

filename = '%s_%s.%s' % (ecab_utils.pathQuote(context.getId()),
                         'template', 'txt')

RESPONSE.setHeader('Content-Disposition', 'inline') # Useful for debugging
#RESPONSE.setHeader('Content-Disposition', 'attachment; filename=' + filename)
RESPONSE.setHeader('Content-Type', 'text/plain')

return output
