# (C) Copyright 2003 Nuxeo SARL <http://nuxeo.com>
# Author: Emmanuel Pietriga (ep@nuxeo.com)
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
"""The NMBMapperTool maps list email addresses to CPSMailBoxer instances
"""

from zLOG import LOG, DEBUG
from Globals import InitializeClass, Persistent, DTMLFile
from AccessControl import ClassSecurityInfo

from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.CMFCorePermissions import View, ManagePortal
from Products.CMFCore.utils import UniqueObject, getToolByName

from Acquisition import aq_parent, aq_inner

from email import message_from_string

from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2

class NMBMapperTool(UniqueObject, PortalFolder, Persistent):
    """Mapping between list email addresses and CPSMailBoxer
    instances + some utility functions"""

    id = 'portal_mailboxermapper'
    meta_type = 'MailBoxerMapper Tool'

    security = ClassSecurityInfo()
    
    _actions = ()

    def __init__(self):
        PortalFolder.__init__(self, self.id)
        self._addr2box = {}

    security.declarePublic('getMailRecipient')
    def getMailRecipient(self, mail=None):
        """given an email source, returns its first recipient"""

        if mail is not None:
            message = message_from_string(mail)
            to_field = message.get('To')
        return to_field

    security.declarePublic('getMailBoxer')
    def getMailBoxer(self, list=None):
        """given a mailing list address, returns the corresponding mailboxer"""

        if list and self._addr2box.has_key(list):
            portal = getToolByName(self, 'portal_url').getPortalObject()
            nmb = portal.restrictedTraverse(self._addr2box.get(list))
            return nmb
        else:
            return None

    security.declarePublic('registerMailBoxer')
    def registerMailBoxer(self, nmb):
        """registers a mailboxer"""
        
        list_addr = getattr(nmb,'mailto',None)
        if list_addr:
            #removing existing mapping is necessary for instance
            #when changing the email address of an existing mailboxer
            portal_url = getToolByName(self, 'portal_url')
            nmb_path = portal_url.getRelativeUrl(nmb)
            self.removeExistingMapping(nmb_path)
            self._addr2box[list_addr] = nmb_path
            self._addr2box = self._addr2box

    security.declarePrivate('removeExistingMapping')
    def removeExistingMapping(self,nmb_path):
        for k,v in self._addr2box.items():
            if v == nmb_path:
                del self._addr2box[k]
                self._addr2box = self._addr2box
                #in theory, we could break after the first removal
                #as only one mapping can exist at some point ; but
                #this is true only in an ideal world where no error
                #occurs ; going through the entire dict seems safer
                #as there might be old entries hanging around as a
                #result of an error happening during registry/unreg

    security.declarePublic('unregisterMailBoxer')
    def unregisterMailBoxer(self, nmb):
        """unregisters a mailboxer"""

        list_addr = getattr(nmb,'mailto',None)
        if self._addr2box.has_key(list_addr):
            del self._addr2box[list_addr]
            self._addr2box = self._addr2box

    security.declarePrivate('notify_nmbreg')
    def notify_nmbreg(self, event_type, object, infos):
        if event_type == 'sys_modify_object':
            self.registerMailBoxer(object)
        elif event_type == 'sys_del_object':
            self.unregisterMailBoxer(object)

    security.declareProtected(ManagePortal, 'manage_purge')
    def manage_purge(self, REQUEST=None):
        """remove all mappings"""
        if REQUEST is not None:
            submit = REQUEST.form.get('submit',None)
            if submit:
                if submit == 'Delete Selected':
                    for list, delete in REQUEST.form.items():
                        if delete == 'on':
                            del self._addr2box[list]
                    self._addr2box = self._addr2box
                elif submit == 'Delete All Mappings':
                    self._addr2box.clear()
                    self._addr2box = self._addr2box
            container = self
            REQUEST.RESPONSE.redirect('%s/manage_mappings'
                                      % (container.absolute_url(),))

    security.declareProtected(ManagePortal, 'getMappings')
    def getMappings(self):
        """get all mappings"""
        
        return self._addr2box
            
    #
    # ZMI
    #

    manage_options = (({'label': 'Overview', 'action': 'manage_overview'},) +
                      ({'label': 'Mappings', 'action': 'manage_mappings'},) +
                      PortalFolder.manage_options)

    # ZMI methods
    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = DTMLFile('dtml/explainNMBMapperTool', globals())
    security.declareProtected(ManagePortal, 'manage_mappings')
    manage_mappings = DTMLFile('dtml/manage_mappings', globals())
    
InitializeClass(NMBMapperTool)
