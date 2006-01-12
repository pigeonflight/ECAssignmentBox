from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import UniqueObject, getToolByName

from config import I18N_DOMAIN

class ECABTool(UniqueObject, SimpleItem):
    """Various utility methods."""

    id = 'ecab_utils'
    portal_type = meta_type = 'ECAssignmentBox Utility Tool'
    
    security = ClassSecurityInfo()

    security.declarePublic('localizeNumber')
    def localizeNumber(self, format, number):
        """A simple method for localized formatting of decimal
        numbers.  Theoretically, one could use locale.format(), but it
        isn't portable enough."""
        if type(number) not in (int, long, float):
            return number
        
        decimalSeparator = self.translate(msgid = 'decimal_separator',
                                          domain = I18N_DOMAIN,
                                          default = '.')
        retval = format % number
        return retval.replace('.', decimalSeparator)
    
    security.declarePublic('getFullNameById')
    def getFullNameById(self, id):
        mtool = self.portal_membership
        member = mtool.getMemberById(id)
        
        if not member:
            return id
        
        try:
            sn        = member.getProperty('sn')
            givenName = member.getProperty('givenName')
        except:
            fullname = member.getProperty('fullname', '')
            
            if fullname == '':
                return id
            
            if fullname.find(' ') == -1:
                return fullname
            
            sn = fullname[fullname.rfind(' ') + 1:]
            givenName = fullname[0:fullname.find(' ')]
            
        return sn + ', ' + givenName

    security.declarePublic('getUserPropertyById')
    def getUserPropertyById(self, id, property=''):
        mtool = self.portal_membership
        member = mtool.getMemberById(id)
        
        try:
            value = member.getProperty(property)
        except:
            return None
        
        return value

    security.declarePublic('isAssignmentBoxType')
    def isAssignmentBoxType(self, obj):
        return hasattr(obj, 'getAssignmentsSummary')

    def findAssignments(self, context, id):
        ct = getToolByName(self, 'portal_catalog')
        ntp = getToolByName(self, 'portal_properties').navtree_properties
        currentPath = None
        query = {}
        
        if context == self:
            currentPath = getToolByName(self, 'portal_url').getPortalPath()
            query['path'] = {'query':currentPath,
                             'depth':ntp.getProperty('sitemapDepth', 2)}
        else:
            currentPath = '/'.join(context.getPhysicalPath())
            query['path'] = {'query':currentPath, 'navtree':1}
        
        query['portal_type'] = ('ECAssignment',)
        #rawresult = ct(**query)
        rawresult = ct(path=currentPath, portal_type='ECAssignment',
                       Creator=id)
        return rawresult


InitializeClass(ECABTool)
