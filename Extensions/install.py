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
from Products.CPSInstaller.CPSInstaller import CPSInstaller
from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent
from Products.CPSCore.CPSWorkflow import \
     TRANSITION_INITIAL_PUBLISHING, TRANSITION_INITIAL_CREATE, \
     TRANSITION_ALLOWSUB_CREATE, TRANSITION_ALLOWSUB_PUBLISHING, \
     TRANSITION_BEHAVIOR_PUBLISHING, TRANSITION_BEHAVIOR_FREEZE, \
     TRANSITION_BEHAVIOR_DELETE, TRANSITION_BEHAVIOR_MERGE, \
     TRANSITION_ALLOWSUB_CHECKOUT, TRANSITION_INITIAL_CHECKOUT, \
     TRANSITION_BEHAVIOR_CHECKOUT, TRANSITION_ALLOW_CHECKIN, \
     TRANSITION_BEHAVIOR_CHECKIN, TRANSITION_ALLOWSUB_DELETE, \
     TRANSITION_ALLOWSUB_MOVE, TRANSITION_ALLOWSUB_COPY
from Products.DCWorkflow.Transitions import TRIGGER_USER_ACTION, \
     TRIGGER_AUTOMATIC
from Products.CPSMailBoxer.CPSMailBoxerPermissions import MailBoxerModerate

def install(self):
    
    ##############################################
    # Create the installer
    ##############################################
    installer = CPSInstaller(self, 'CPSMailBoxer')
    installer.log("Starting CPSMailBoxer install")
    nmb = 'CPSMailBoxer'
    nmbf = 'CPSMailBoxerFolder'
    nmba = 'CPSMailArchive'
    typestool = installer.portal.portal_types

    #################################################
    # MailBoxer-specific roles and permissions
    #################################################
    installer.log("Checking specific roles and permissions")
    perms = {
        MailBoxerModerate:
        ('Manager', 'Owner', 'WorkspaceManager', 'MailBoxerModerator',
         'SectionManager', 'SectionReviewer',),
        }
    installer.verifyRoles(('MailBoxerModerator',))
    installer.setupPortalPermissions(perms)

    ##########################################
    # SKINS
    ##########################################
    skins = {'cpsmailboxer_default':
             'Products/CPSMailBoxer/skins/cpsmailboxer_default'}
    installer.verifySkins(skins)
    installer.resetSkinCache()

    ##########################################
    # PORTAL TYPES
    ##########################################
    installer.log("Checking portal types")
    installer.log(" Registering portal types: %s %s" % (nmb, nmbf))
    ptypes_installed = typestool.objectIds()
    if nmb in ptypes_installed:
        typestool.manage_delObjects(nmb)
        installer.log("  Type %s Deleted" % (nmb,))
    if nmbf in ptypes_installed:
        typestool.manage_delObjects(nmbf)
        installer.log("  Type %s Deleted" % (nmbf,))
    typestool.manage_addTypeInformation(
        id=nmb,
        add_meta_type='Factory-based Type Information',
        typeinfo_name='CPSMailBoxer: CPSMailBoxer')
    typestool[nmb].manage_changeProperties(
        title='portal_type_CPSMailBoxer_title',
        description='portal_type_CPSMailBoxer_description',
        content_meta_type=nmb,
        filter_content_types=1)
    typestool.manage_addTypeInformation(
        id=nmbf,
        add_meta_type='Factory-based Type Information',
        typeinfo_name='CPSMailBoxer: CPSMailBoxerFolder')
    typestool[nmbf].manage_changeProperties(
        title='portal_type_CPSMailBoxerFolder_title',
        description='portal_type_CPSMailBoxerFolder_description',
        content_meta_type=nmbf,
            filter_content_types=1)


    installer.log("Checking Mapper Tool")
    if installer.portalHas('portal_mailboxermapper'):
        installer.logOK()
    else:
        installer.log(" Creating CPSMailBoxerMapper Tool "
                 "(portal_mailboxermapper)")
        installer.portal.manage_addProduct['CPSMailBoxer'].manage_addTool(
            'MailBoxerMapper Tool')
    installer.log("Verifying Event service tool")
    objs = installer.portal.portal_eventservice.objectValues()
    subscribers = []
    for obj in objs:
        subscribers.append(obj.subscriber)
    if 'portal_mailboxermapper' in subscribers:
        installer.logOK()
    else:
        installer.log(" Creating portal_mailboxermapper subscribers")
        installer.portal.portal_eventservice.manage_addSubscriber(
            subscriber='portal_mailboxermapper',
            action='nmbreg',
            meta_type='CPSMailBoxer',
            event_type='*',
            notification_type='synchronous')

        installer.log("Checking workflows")

    ##########################################
    # WORKFLOW DEFINITION
    ##########################################
    # workflow for MailBoxer mail archives
    wfdef = {'wfid': 'mail_archive_wf',
             'permissions': (View, ModifyPortalContent),
             'state_var': 'review_state'}
    
    wfstates = {
        'created': {
            'title': 'Created',
            'transitions': ('auto_publish', 'auto_moderate'),
            'permissions': {View: ('Manager', 'Owner', 'WorkspaceManager',
                                   'SectionManager', 'SectionReviewer',
                                   'MailBoxerModerator'),
                            ModifyPortalContent: ('Manager', 'Owner',
                                                  'WorkspaceManager',
                                                  'SectionManager',
                                                  'SectionReviewer',
                                                  'MailBoxerModerator')},
            },
        'pending': {
            'title': 'Awaiting acceptance',
            'transitions': ('publish', 'reject'),
            'permissions': {View: ('Manager', 'Owner', 'WorkspaceManager',
                                   'SectionManager', 'SectionReviewer',
                                   'MailBoxerModerator'),
                            ModifyPortalContent: ('Manager', 'Owner',
                                                  'WorkspaceManager',
                                                  'SectionManager',
                                                  'SectionReviewer',
                                                  'MailBoxerModerator')},
            },
        'published': {
            'title': 'Public',
            'transitions': (),
            'permissions': {View: ('Manager', 'Owner', 'WorkspaceManager',
                                   'WorkspaceMember', 'WorkspaceReader',
                                   'SectionManager', 'SectionReviewer',
                                   'SectionReader',
                                   'MailBoxerModerator'),
                            ModifyPortalContent: ('Manager',)},
            },
        'rejected': {
            'title': 'Rejected',
            'transitions': (),
            'permissions': {View: ('Manager', 'Owner', 'WorkspaceManager',
                                   'SectionManager', 'SectionReviewer',
                                   'MailBoxerModerator'),
                            ModifyPortalContent: ('Manager',)},
            }
        }
    
    wftransitions = {
        'create': {
            'title': 'Initial creation',
            'new_state_id': 'created',
            'transition_behavior': (TRANSITION_INITIAL_CREATE, ),
            'clone_allowed_transitions': None,
            'after_script_name': 'msg_edit',
            'trigger_type': TRIGGER_USER_ACTION,
            'props': {'guard_permissions': '',
                      'guard_roles':'',
                      'guard_expr':''},
            },
        'auto_publish': {
            'title': 'No moderation, publishing',
            'new_state_id': 'published',
            'trigger_type': TRIGGER_AUTOMATIC,
            'clone_allowed_transitions': None,
            'props': {'guard_permissions': '',
                      'guard_roles': '',
                      'guard_expr': 'python:container.getContent().moderation_mode == 0'},
            },
        'auto_moderate': {
            'title': 'Moderating',
            'new_state_id': 'pending',
            'trigger_type': TRIGGER_AUTOMATIC,
            'clone_allowed_transitions': None,
            'props': {'guard_permissions': '',
                      'guard_roles': '',
                      'guard_expr': 'python:container.getContent().moderation_mode == 1'},
            },
        'publish': {
            'title': 'Publishing post',
            'new_state_id': 'published',
            'clone_allowed_transitions': None,
            'trigger_type': TRIGGER_USER_ACTION,
            'props': {'guard_permissions': 'MailBoxer Moderate',
                      'guard_roles':'',
                      'guard_expr':''},
            },
        'reject': {
            'title': 'Rejecting post',
            'new_state_id': 'rejected',
            'clone_allowed_transitions': None,
            'trigger_type': TRIGGER_USER_ACTION,
            'props': {'guard_permissions': 'MailBoxer Moderate',
                      'guard_roles':'',
                      'guard_expr':''},
            },
        }
    
    wfscripts = {
        'msg_edit': {
        '_owner': None,
        '_proxy_roles': ['Manager'],
        'script': """\
##parameters=state_change
object = state_change.object
object_content = object.getContent()
title = state_change.kwargs.get('Title', '')
mailFrom = state_change.kwargs.get('mailFrom', '')
mailSubject = state_change.kwargs.get('mailSubject', '')
mailDate = state_change.kwargs.get('mailDate', '')
mailBody = state_change.kwargs.get('mailBody', '')
attachments = state_change.kwargs.get('attachments', {})

kw = {'Title': title,
      'mailFrom': mailFrom,
      'mailSubject': mailSubject,
      'mailDate': mailDate,
      'mailBody': mailBody}
object.getEditableContent().edit(**kw)

layout_id = 'cps_mailarchive_flexible'
widget_type = 'mailAttachment'
for widget_id, attchment in attachments.items():
    object_content.flexibleAddWidget(layout_id, widget_type)
object.getEditableContent().edit(**attachments)
"""
        },
        }
    
    wfvariables = {
        'Title': {
            'description': 'mail subject',
            'default_expr': "python:state_change.kwargs.get('Title', '')",
            'for_status': 1,
            'update_always': 1,
            },
        'mailFrom': {
            'description': '',
            'default_expr': "python:state_change.kwargs.get('mailFrom', '')",
            'for_status': 1,
            'update_always': 1,
            },
        'mailSubject': {
            'description': '',
            'default_expr': "python:state_change.kwargs.get('mailSubject', '')",
            'for_status': 1,
            'update_always': 1,
            },
        'mailBody': {
            'description': '',
            'default_expr': "python:state_change.kwargs.get('mailBody', '')",
            'for_status': 1,
            'update_always': 1,
            },
        'mailDate': {
            'description': '',
            'default_expr': "python:state_change.kwargs.get('mailDate', '')",
            'for_status': 1,
            'update_always': 1,
            },
        'attachments': {
            'description': '',
            'default_expr': "python:state_change.kwargs.get('attachments', '')",
            'for_status': 1,
            'update_always': 1,
            },
        }

    installer.verifyWorkflow(wfdef, wfstates, wftransitions,
                               wfscripts, wfvariables)
    
    ws_chains = {'CPSMailBoxer': 'workspace_folder_wf', 'CPSMailArchive': 'mail_archive_wf'}
    se_chains = {'CPSMailBoxer': 'section_folder_wf', 'CPSMailArchive': 'mail_archive_wf'}
    installer.verifyLocalWorkflowChains(installer.portal['workspaces'],
                                        ws_chains)
    installer.verifyLocalWorkflowChains(installer.portal['sections'],
                                        se_chains)
    
    ##############################################
    # i18n support
    ##############################################
    installer.setupTranslations()

    ##############################################
    # Finished!
    ##############################################
    installer.finalize()
    installer.log("End of CPSMailBoxer install")
    return installer.logResult()
