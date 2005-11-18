def getFullNameById(obj, id):
    mtool = obj.portal_membership
    member = mtool.getMemberById(id)
    
    try:
        sn        = member.getProperty('sn')
        givenName = member.getProperty('givenName')
    except:
        fullname = member.getProperty('fullname', '')
        
        if fullname.find(' ') == -1:
            return fullname
        
        sn = fullname[fullname.rfind(' ') + 1:]
        givenName = fullname[0:fullname.find(' ')]
    
    return sn + ', ' + givenName
