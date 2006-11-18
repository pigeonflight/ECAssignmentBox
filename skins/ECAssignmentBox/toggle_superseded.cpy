## Script (Python) "toggle_superseded"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

# This script redirects to the same location it got called from,
# except that the value of 'show_superseded' in the query string is
# negated.

I18N_DOMAIN = 'eduComponents'

REQUEST  = container.REQUEST
RESPONSE = REQUEST.RESPONSE
ecab_utils = context.ecab_utils

oquery = ecab_utils.parseQueryString(REQUEST.QUERY_STRING)
query = {}
# "unlistify" the values that `parseQueryString' returned
for k,v in oquery.items():
    query[k]=v[0]

# Negate value of 'show_superseded'
showSuperseded = query.get('show_superseded', None)
if showSuperseded:
    showSuperseded = ''
else:
    showSuperseded = 1
query['show_superseded'] = showSuperseded

#query['portal_status_message'] = query.items()

target = context.getActionInfo('object/all_assignments')['url']
return RESPONSE.redirect('%s?%s' % (target, ecab_utils.urlencode(query)))
