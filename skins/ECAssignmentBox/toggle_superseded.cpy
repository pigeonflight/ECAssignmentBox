## Script (Python) "toggle_superseded"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

I18N_DOMAIN = 'eduComponents'

REQUEST  = container.REQUEST
RESPONSE = REQUEST.RESPONSE

showSuperseded = REQUEST.get('show_superseded', None)

print showSuperseded

if showSuperseded:
    showSuperseded = ''
else:
    showSuperseded = 1

REQUEST.set('show_superseded', showSuperseded)

#print REQUEST
#return printed

return state