# (C) Copyright 2002 Nuxeo SARL <http://nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View
from Products.CPSDocument.CPSDocument import CPSDocument

class CPSMailArchive(CPSDocument):
    """
    The base class for all MailArchives.
    """

    # Too ease debugging
    meta_type = 'CPSMailArchive'
    portal_type = meta_type

    security = ClassSecurityInfo()

    security.declareProtected('View', 'Creator')
    def Creator(self):
        """Return the emitter of the email message.
        """
        return getattr(self, 'mailFrom',
                       CPSDocument.Creator(self))

    
InitializeClass(CPSMailArchive)


def addInstance(container, id, REQUEST=None, **kw):
    """Factory method
    """

    instance = CPSMailArchive(id, **kw)
    container._setObject(id, instance)

    # It's mandatory then after to get the object through its parent, for the
    # object to have a reference on its parent. Having the object know about its
    # parent is mandatory if one wants to be able to call some methods like
    # manage_addProduct() on it.
    #object = getattr(container, id)

    if REQUEST:
        object = container._getOb(id)
        LOG(logKey, DEBUG, "object = %s" % object)
        REQUEST.RESPONSE.redirect(object.absolute_url() + '/manage_main')

