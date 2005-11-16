## Script (Python) "sortable_name"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=member=''
##title=Create a sortable name for a member object.
##

# $Id$

try:
    sn        = member.getProperty('sn')
    givenName = member.getProperty('givenName')
except:
    fullname = member.getProperty('fullname', '')

    if fullname.find(' ') == -1:
        return fullname

    sn = fullname[fullname.rfind(' '):]
    givenName= fullname[0:fullname.find(' ')]

return sn + ', ' + givenName


