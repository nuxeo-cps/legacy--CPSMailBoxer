##parameters=user_name

from Products.CMFCore.utils import getToolByName
from zLOG import LOG, DEBUG

logKey = 'getEmailAddress'

membersDirectory = getToolByName(context, 'portal_directories').members
entry = membersDirectory.getEntry(user_name)
#LOG(logKey, DEBUG, "entry = %s" % str(entry))

email = entry.get('email', None)
#LOG(logKey, DEBUG, "email = %s" % email)

return email
