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

# Basic Installer for Cpsmailboxer

# IMPORTANT: this installer only registers the CPSMailBoxer portal type
# and creates the appropriate skin entries. It does not associate any
# workflow nor does it change workspace/section allowed content types
# to accept MailBoxer objects, as this would be making the assumption
# that we are relying on the std workspace/section hierarchy, which
# is not necessarily the case.
# This should thus be done in your own installer

from Products.CPSDefault.Installer import BaseInstaller

class CPSMailBoxerInstaller(BaseInstaller):

    SKINS = (('cpsmailboxer_default', 
              'Products/CPSMailBoxer/skins/cpsmailboxer_default'),)

    def install(self):
        self.log("Starting CPSMailBoxer install")
        self.product_name = 'CPSMailBoxer'
        self.nmb = 'CPSMailBoxer'
        self.nmbf = 'CPSMailBoxerFolder'
        self.setupCpsDocumentDependantSkins(self.SKINS)
        self.typestool = self.portal.portal_types
        self.setupPortalTypes()
        self.setupNMBMapperTool()
        self.setupTranslations()
        self.configurePlaceFullWorkflow()

    def setupPortalTypes(self):
        nmb = self.nmb
        nmbf = self.nmbf
        self.log(" Registering portal types: %s %s" % (nmb, nmbf))
        ptypes_installed = self.typestool.objectIds()
        if nmb in ptypes_installed:
            self.typestool.manage_delObjects(nmb)
            self.log("  Type %s Deleted" % (nmb,))
        if nmbf in ptypes_installed:
            self.typestool.manage_delObjects(nmbf)
            self.log("  Type %s Deleted" % (nmbf,))
        self.typestool.manage_addTypeInformation(
            id=nmb,
            add_meta_type='Factory-based Type Information',
            typeinfo_name='CPSMailBoxer: CPSMailBoxer')
        self.typestool[nmb].manage_changeProperties(
            title='portal_type_CPSMailBoxer_title',
            description='portal_type_CPSMailBoxer_description',
            content_meta_type=nmb,
            filter_content_types=1)
        self.typestool.manage_addTypeInformation(
            id=nmbf,
            add_meta_type='Factory-based Type Information',
            typeinfo_name='CPSMailBoxer: CPSMailBoxerFolder')
        self.typestool[nmbf].manage_changeProperties(
            title='portal_type_CPSMailBoxerFolder_title',
            description='portal_type_CPSMailBoxerFolder_description',
            content_meta_type=nmbf,
            filter_content_types=1)
        
        self.log("Add our portal type id to allowed portal type of workspaces")

    def setupNMBMapperTool(self):
        self.log("Installing CPSMailBoxer Mapper Tool")
        if self.portalHas('portal_mailboxermapper'):
            self.logOK()
        else:
            self.log(" Creating CPSMailBoxerMapper Tool "
                     "(portal_mailboxermapper)")
            self.portal.manage_addProduct['CPSMailBoxer'].manage_addTool(
                'MailBoxerMapper Tool')
        self.log("Verifying Event service tool")
        objs = self.portal.portal_eventservice.objectValues()
        subscribers = []
        for obj in objs:
            subscribers.append(obj.subscriber)
        if 'portal_mailboxermapper' in subscribers:
            self.logOK()
        else:
            self.log(" Creating portal_mailboxermapper subscribers")
            self.portal.portal_eventservice.manage_addSubscriber(
                subscriber='portal_mailboxermapper',
                action='nmbreg',
                meta_type='CPSMailBoxer',
                event_type='*',
                notification_type='synchronous')

    def configurePlaceFullWorkflow(self):
        """
        Configure the workspaces placefull workflow
        """
        self.log("Installing Workflow chain in placefull workflow "
                 "configuration of root of Workspaces and sections")
        wf_config = getattr(self.portal.workspaces, 
                            '.cps_workflow_configuration')
        wf_config.manage_addChain(portal_type=self.nmb, 
                                  chain='workspace_folder_wf')
        wf_config = getattr(self.portal.sections, 
                            '.cps_workflow_configuration')
        wf_config.manage_addChain(portal_type=self.nmb, 
                                  chain='section_folder_wf')

        
def install(self):
    installer = CPSMailBoxerInstaller(self)
    installer.install()
    return installer.logResult()
