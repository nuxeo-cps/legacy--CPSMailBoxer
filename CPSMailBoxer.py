# -*- coding: ISO-8859-15 -*-
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

import Globals
import multifile, difflib, re, mimetools, rfc822, cgi, smtplib, mimify,\
       random, md5
from DateTime import DateTime
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from AccessControl.User import UnrestrictedUser
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager

from OFS.PropertyManager import PropertyManager

from Products.CMFDefault.SkinnedFolder import SkinnedFolder
from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent,\
     ChangePermissions
from Products.CMFCore.utils import getToolByName

from Products.CPSCore.EventServiceTool import getEventService

from Products.MailBoxer import MailBoxer
from Products.MailBoxer.MailBoxerTemplates import MailBoxerTemplates

from CPSMailBoxerFolder import CPSMailBoxerFolder
from CPSMailBoxerBoxes import CPSMAILBOXER_BOXES
from CPSMailBoxerPermissions import MailBoxerModerate

from email.MIMEText import MIMEText

from zLOG import LOG,DEBUG,ERROR

import traceback
from StringIO import StringIO

TRUE = "TRUE"
FALSE = "FALSE"

factory_type_information = (
    {'id': 'CPSMailBoxer',
     'title': 'portal_type_CPSMailBoxer_title',
     'description': 'portal_type_CPSMailBoxer_description',
     'meta_type': 'CPSMailBoxer',
     'icon': 'MailHost_icon.gif',
     'product': 'CPSMailBoxer',
     'factory': 'addCPSMailBoxer',
     'immediate_view': 'cpsmailboxer_edit_form',
     'allow_discussion': 0,
     'filter_content_types': 0,
     'cps_display_as_document_in_listing': 1,
     'actions': ({'id': 'view',
                  'name': 'action_view',
                  'action': 'folder_view',
                  'permissions': (View,)},
                 {'id': 'subscribe',
                  'name': 'action_subscribe',
                  'action': 'cpsmailboxer_subscribe_form',
                  'permissions': (View)},  # Is this permission OK ?
                 {'id': 'edit',
                  'name': 'action_modify_prop',
                  'action': 'cpsmailboxer_edit_form',
                  'permissions': (ModifyPortalContent,)},
                 {'id': 'edit_members',
                  'name': 'action_manage_members',
                  'action': 'cpsmailboxer_members_edit_form',
                  'permissions': (MailBoxerModerate,)},
                 {'id': 'moderate_msgs',
                  'name': 'action_moderate_msgs',
                  'action': 'cpsmailboxer_moderation_form',
                  'permissions': (MailBoxerModerate,)},
                 {'id': 'creatnletter',
                  'name': 'Create Newsletter',
                  'action': 'cpsmailboxer_newsletter_create_form',
                  'permissions': (MailBoxerModerate,)},
                 {'id': 'create',
                  'name': 'Create',
                  'action': 'cpsmailboxer_create_form',
                  'visible': 0,
                  'permissions': (ModifyPortalContent)},
                 {'id': 'localroles',
                  'name': 'action_local_roles',
                  'action': 'mb_localrole_form',
                  'permissions': (ChangePermissions,),
                  }
                ),
                'cps_proxy_type':None,
                'cps_is_searchable':1,
     },
)

class CPSMailBoxer(MailBoxer, SkinnedFolder, PropertyManager):
    """
    Mailing list managment and archive for Nuxeo CPS
    """

    meta_type = 'CPSMailBoxer'

    security = ClassSecurityInfo()

    _properties = (
        {'id':'description', 'type':'text', 'mode':'w', 'label':'Description'},
        {'id':'moderation_mode', 'type':'boolean', 'mode':'w', 'label':'Moderation'},
    ) + MailBoxer._properties

    title = ''
    moderation_mode = 0
    _queue = {}

    def __init__(self, id, title=''):
        """
        CPSMailBoxer constructor
        """
        MailBoxer.__init__(self, id, title)
        self._setId(id)

    security.declareProtected(ModifyPortalContent, 'edit')
    def edit(self, **kw):
        """
        Modify object properties
        @return: None
        @rtype: None

        @type kw: C{dict}
        @param kw: Keyword parameters, properties to changed
        """
        self.manage_changeProperties(**kw)
        evtool = getEventService(self)
        evtool.notify('sys_modify_object', self, {})
        self.reindexObject()


    ###
    # Public method to be called via smtp2zope-gateway
    ##

    security.declarePublic('manage_mailboxer')
    def manage_mailboxer(self, REQUEST):
        """ Default for a all-in-one mailinglist-workflow.

            Handles (un)subscription-requests and
            checks for loops etc & bulks mails to list.

            @param REQUEST: REQUEST Zope object
            @type REQUEST: C{REQUEST}

        """
        
        try:
            # XXX: there might be a lighter solution than
            # setting Manager role for this method
            # but if we don't, we get security exceptions
            # in several places (anonymous has no View_permission
            # and no Add_portal_content_permission on CPSMailBoxer)
            class CPSUnrestrictedUser(UnrestrictedUser):
                """Unrestricted user that still has an id.

                Taken from CPSMembershipTool
                """

                def getId(self):
                    """Return the ID of the user."""
                    return self.getUserName()

            mtool = getToolByName(self, 'portal_membership')
            old_user = getSecurityManager().getUser()

            tmp_user = CPSUnrestrictedUser('root', '',
                                           ['Manager', 'Member'], '')
            tmp_user = tmp_user.__of__(mtool.acl_users)
            newSecurityManager(None, tmp_user)

            if self.checkMail(REQUEST):
                newSecurityManager(None, old_user)
                return FALSE

            # Check for subscription/unsubscription-request
            if self.requestMail(REQUEST):
                newSecurityManager(None, old_user)
                return TRUE

            # Process the mail...
            self.processMail(REQUEST)
            newSecurityManager(None, old_user)
            return TRUE
        except Exception ,e :
            s = StringIO()
            traceback.print_exc(file=s)
            LOG('Error processing mail for CPSMailBoxer: ',
                ERROR,
                'traceback:\n%s' % s.getvalue())


    def manage_addFolder(self, id, title=''):
        """
        Add a CPSMailBoxerFolder insted of a normal Folder.

        @return: C{None}
        @rtype: C{None}

        """
        ob = CPSMailBoxerFolder(id, title)
        self._setObject(id, ob)

    def manage_addYearFolder(self, archive, year, title):
        """
        Add a CPSMailBoxerFolder for year archive folder
        @return: the Year archive folder
        @rtype: L{CPSMailBoxerFolder}

        @param archive: The archive folder
        @type archive: L{CPSMailBoxerFolder}

        @param id: The created object id in container
        @type id: C{string}

        @param title: The created object title
        @type title: C{string}

        @note: Create the Year archive or return the exists
        """
        # do we have a year folder already?
        if not hasattr(archive, year):
            archive.manage_addProduct['CPSMailBoxer'].addCPSMailBoxerFolder(id=year, title=title, boxes=('mb_content',))
        yearFolder = getattr(archive, year)

        return yearFolder

    def manage_addMonthFolder(self, yearFolder, month, title):
        """
        Add a CPSMailBoxerFolder for month archive folder
        """
        # do we have a month folder already?
        if not hasattr(yearFolder, month):
            yearFolder.manage_addProduct['CPSMailBoxer'].addCPSMailBoxerFolder(id=month, title=title, boxes=('mb_content',))
        monthFolder = getattr(yearFolder, month)

        return monthFolder

    security.declarePublic('manage_addMember')
    def manage_addMember(self, email):
        """ Add member to maillist. """

        memberlist = list(self.getValueFor('maillist'))
        if email.lower() not in self.lowerList(memberlist):
            memberlist.append(email)
            memberlist.sort()
            self.setValueFor('maillist', memberlist)
            return email
        else:
            raise KeyError, 'email exists'

    def sendtoList(self, context, ffrom=None, fto=None, subject='Newsletter',
                   texte=''):
        """
        Send a message to the members of the list

        @return: C{None}
        @rtype: C{none}
        @param ffrom: 'From' e-mail address of the sended e-mails.
        @type ffrom: C{string}
        @param fto: 'To' e-mail address of the sended e-mails
        @type fto: C{string}
        @param subject: 'Subject' of the sended e-mails
        @type subject: C{string}
        @param texte: Body of the sended e-mails.
        @param texte: C{string}


        @note: send emails
        """

        if ffrom is None:
            ffrom = self.moderator[0]
        if fto is None:
            fto = self.mailto
        msg = MIMEText(texte, _charset="iso-8859-1")
        msg.add_header('Subject', subject)
        msg.add_header('From', ffrom)
        msg.add_header('To', fto)
        req = context.REQUEST
        req['Mail'] = msg.as_string()
        self.listMail(req)

    def manage_addMail(self, Mail):
        """
        Create a Mail object in the archive tree structure
        Create year/month tree branch if they didn't exist

        @return: Created Mail object
        @rtype: L{CPSMailBoxerFolder}

        @param Mail: E-mail strucured to be stored
        @type Mail: L{CPSMailBoxerFolder}

        """

        archive = self.restrictedTraverse(self.getValueFor('storage'),
                                          default=None)

        # no archive available? then return immediately
        if archive is None:
            return None

        (header, body) = self.splitMail(Mail)

        # if 'keepdate' is set, get date from mail,
        if self.getValueFor('keepdate'):
            timetuple = rfc822.parsedate_tz(header.get('date'))
            time = DateTime(rfc822.mktime_tz(timetuple))
        # ... take our own date, clients are always lying!
        else:
            time = DateTime()

        # now let's create the date-path (yyyy/yyyy-mm)
        year  = str(time.year())                  # yyyy
        month = "%s-%s" % (year, str(time.mm()))  # yyyy-mm

        yearFolder = self.manage_addYearFolder(archive, year, year)
        monthFolder = self.manage_addMonthFolder(yearFolder, month, month)

        # let's create the mailObject
        mailFolder = monthFolder

        subject = self.mime_decode_header(header.get('subject', 'No Subject'))
        sender = self.mime_decode_header(header.get('from','No From'))
        title = "%s / %s" % (subject, sender)

        # search a free id for the mailobject
        id = time.millis()
        while hasattr(mailFolder, str(id)):
            id = id + 1
            
        id = str(id)
        
        mailObjectProxy = self.addMailBoxerMail(mailFolder, id, title, sender,
                                                subject, time, Mail)
        
        return mailObjectProxy

    def addMailBoxerMail(self, mailFolder, id, title, sender, subject, time, Mail):
        """
        """
        if hasattr(mailFolder, 'fake'):
            mailFolder.manage_delObjects(['fake'])
        mailFolder.invokeFactory(type_name='CPSMailArchive', id='fake')
        fake = getattr(mailFolder, 'fake')
        
        # unpack attachments
        (TextBody, ContentType, HtmlBody) =  self._unpackMultifile(fake,
                                                     multifile.MultiFile(
                                                      StringIO(Mail)))

        # ContentType is only set for the TextBody
        if ContentType:
            body = TextBody
        else:
            body = self.HtmlToText(HtmlBody)

        files = {}
        widget_type = 'mailAttachment'
        layout_id = 'cps_mailarchive_flexible'
        fakeObject = getattr(mailFolder, 'fake').getContent()
        attachedFiles = fake.objectValues()
        for attachment in attachedFiles:
            widget_id = str(fakeObject.flexibleAddWidget(layout_id, widget_type))
            files[widget_id] = attachment
        mailFolder.manage_delObjects(['fake'])

        mailFolder.invokeFactory(type_name='CPSMailArchive', id=id,
                                 Title=subject, mailFrom=sender,
                                 mailSubject=subject,
                                 mailDate=time, mailBody=body,
                                 attachments=files)

        mailObjectProxy = getattr(mailFolder, id)
        mailObject = mailObjectProxy.getContent()

        # insert header if a regular expression is set and matches
        headers_regexp = self.getValueFor('headers')
        if headers_regexp:
            msg = mimetools.Message(StringIO(Mail))
            headers = []
            for (key, value) in msg.items():
                if re.match(headers_regexp, key, re.IGNORECASE):
                    headers.append('%s: %s' % (key, value.strip()))

            mailObject.manage_addProperty('mailHeader', headers, 'lines')

        return mailObjectProxy

    def mail_handler(self, mb, REQUEST, mail='', body=''):
        mail_archive_proxy = self.archiveMail(REQUEST)
        mail_archive = mail_archive_proxy.getContent()
        if self.moderation_mode:
            self.queueMail(REQUEST, mail_archive)
        else:
            self.listMail(REQUEST, mail_archive=mail_archive,
                          proxy=mail_archive_proxy)

    def archiveMail(self, REQUEST):
        # store mail in the archive? get context for the mail...
        Mail = REQUEST['Mail']
        mail_archive_proxy = None
        mail_archive_proxy = self.manage_addMail(Mail)
        if mail_archive_proxy is None:
            mail_archive_proxy = self
        return mail_archive_proxy

    security.declareProtected(MailBoxerModerate, 'resetQueue')
    def resetQueue(self):
        self._queue = {}

    security.declareProtected(MailBoxerModerate, 'getQueue')
    def getQueue(self):
        return self._queue

    def queueMail(self, REQUEST, mail_archive):
        mail_url = getToolByName(self, 'portal_url').getRelativeUrl(mail_archive)
        queue = self._queue
        queue[mail_url] = REQUEST['Mail']
        self._queue = queue
        
    def rejectMail(self, mail_archive):
        mail_url = getToolByName(self, 'portal_url').getRelativeUrl(mail_archive)
        if self._queue.has_key(mail_url):
            del self._queue[mail_url]

    def acceptMail(self, mail_archive, proxy):
        mail_url = getToolByName(self, 'portal_url').getRelativeUrl(mail_archive)
        if self._queue.has_key(mail_url):
            REQUEST = {}
            REQUEST['Mail'] = self._queue.get(mail_url)
            del self._queue[mail_url]
            self.listMail(REQUEST, mail_archive=mail_archive, proxy=proxy)

    def listMail(self, REQUEST, mail_archive=None, proxy=None):

        # Send a mail to all members of the list. 

        Mail = REQUEST['Mail']

        if mail_archive is None:
            context = self
        else:
            context = mail_archive

        (header, body) = self.splitMail(Mail)

        # plainmail-mode? get the plain-text of mail...
        if self.getValueFor('plainmail'):          
            (TextBody, ContentType, HtmlBody) = self._unpackMultifile(None, 
                                                   multifile.MultiFile(
                                                    StringIO(Mail)))
            if ContentType:
                header['content-type'] = ContentType
                body = TextBody
            else:
                charset = ""
                match = re.search('(?is)<meta.*?content="text/html;[\s]*charset=([^"]*?)".*?>',
                                                                      HtmlBody)
                if match:
                    charset="charset=%s;" % match.group(1)
                header['content-type'] = 'text/plain;%s' % charset
                body = self.HtmlToText(HtmlBody)
                
        
        # get custom header & footer
        (customHeader, customBody) = self.splitMail(
            self.mail_header(context,
                             REQUEST,
                             getValueFor=self.getValueFor, 
                             title=self.getValueFor('title'),
                             mail=header, 
                             body=body,
                             mime_decode_header=self.mime_decode_header).strip())
        
        customFooter = self.mail_footer(context,
                                        REQUEST,
                                        getValueFor=self.getValueFor,
                                        title=self.getValueFor('title'),
                                        mail=header, 
                                        body=body).strip()
        
        
        # Patch msg-headers with customHeaders
        msg = mimetools.Message(StringIO(Mail))
        
        for hdr in customHeader.keys():
            if customHeader[hdr]:
                msg[hdr.capitalize()]=customHeader[hdr]
            else:
                del msg[hdr]
        
        newHeader = ''.join(msg.headers)

        # If customBody is not empty, use it as new mailBody
        if customBody.strip():
            body=customBody

        newMail = "%s\r\n%s\r\n%s" % (newHeader, body, customFooter)

        # Get members
        memberlist = self.getValueFor('maillist')
        
        # Remove "blank" / corrupted / doubled entries
        maillist=[]
        for email in memberlist:
            if '@' in email and email not in maillist:
                maillist.append(email)

        batchsize = self.getValueFor('batchsize')

        # if no returnpath is set, use first moderator as returnpath
        returnpath=self.getValueFor('returnpath')
        if not returnpath:
            returnpath = self.getValueFor('moderator')[0]

        # bulk mail. return-path is first moderator.
        try:
            # open smtp-connection
            smtpserver = smtplib.SMTP(self.MailHost.smtp_host, 
                                      int(self.MailHost.smtp_port))
                
            # start batching mails to smtp-server
            while maillist:
                # if no batchsize is set (default) 
                # or batchsize is greater than maillist,
                # bulk all mails in one batch, 
                # otherwise bulk only 'batch'-mails at once
                if (batchsize == 0) or (batchsize > len(maillist)):
                    batch = len(maillist)
                else:
                    batch = batchsize

                # bulk mails to smtp-server
                smtpserver.sendmail(returnpath, maillist[0:batch], newMail)
                # remove already bulked addresses
                maillist = maillist[batch:]

            # close connection
            smtpserver.quit()
        
        except Exception, e:
            LOG('MailBoxer', ERROR, e)

        if self.getValueFor('archived') == self.archive_options[0]:
            # delete mail if archive is set to No archive
            proxy_rpath = getToolByName(self, 'portal_url').getRelativeUrl(proxy)
            month_folder_rpath = proxy_rpath[:proxy_rpath.rfind('/')]
            month_folder_proxy = self.restrictedTraverse(month_folder_rpath)
            month_folder_proxy.manage_delObjects([proxy.id])


    def notifyReject(self, proxy_msg, comment=''):
        """Notify sender that his email has been rejected by moderator"""
        
        doc = proxy_msg.getContent()
        sender_email = doc.mailFrom
        subject = doc.mailSubject
        date = doc.mailDate.strftime('%d/%m/%y %H:%M')
        text = doc.mailBody

        portal = getToolByName(self, 'portal_url').getPortalObject()
        cpsmcat = portal.Localizer.default

        nmb_mail_reject_1 = cpsmcat('nmb_mail_reject_1').encode('ISO-8859-15', 'ignore')
        nmb_mail_reject_2 = cpsmcat('nmb_mail_reject_2').encode('ISO-8859-15', 'ignore')
        nmb_mail_reject_3 = cpsmcat('nmb_mail_reject_3').encode('ISO-8859-15', 'ignore')
        nmb_mail_reject_4 = cpsmcat('nmb_mail_reject_4').encode('ISO-8859-15', 'ignore')
        nmb_mail_reject_5 = cpsmcat('nmb_mail_reject_5').encode('ISO-8859-15', 'ignore')
        nmb_mail_reject_6 = cpsmcat('nmb_mail_reject_6').encode('ISO-8859-15', 'ignore')
        
        body = "%s '%s' %s %s %s" % (nmb_mail_reject_1, subject, nmb_mail_reject_2,
                                        date, nmb_mail_reject_3)
        subject = "%s %s" % (nmb_mail_reject_4, subject)
        if comment:
            body +=  " %s\n%s" % (nmb_mail_reject_5, comment)
        else:
            body += "."
        body += "\n\n%s\n\n%s" % (nmb_mail_reject_6, text)
        self.sendEmail(portal, from_address=getattr(portal,
                                                    'email_from_address'),
                       subject=subject,
                       body=self.textwrap(body, 72),
                       mto=[sender_email])

    def notifyModerate(self, nmb, proxy_msg):
        """Notify moderators that a new mail is pending"""

        portal_url = getToolByName(self, 'portal_url')
        portal = portal_url.getPortalObject()
        msg_rpath = portal_url.getRelativeUrl(proxy_msg)

        if not msg_rpath.endswith('fake'):
            users_with_role = nmb.getMBLocalRoles()[0]
            usr_names = []
            for usr_name in users_with_role.keys():
                if usr_name.startswith('user:'):
                    usr_names.append(usr_name[5:])
            #XXX: maybe we should handle groups here too...
            moderator_emails = []
            for usr_name in usr_names:
                usr = portal.portal_membership.getMemberById(usr_name)
                if usr.has_permission(MailBoxerModerate, nmb):
                    moderator_emails.append(usr.getProperty('email'))
            filtered_emails = []
            for email in moderator_emails:
                if email not in filtered_emails:
                    filtered_emails.append(email)
            if len(filtered_emails) == 0:
                filtered_emails = self.getValueFor('moderator')
            cpsmcat = portal.Localizer.default
            moderation_url = "%s/cpsmailboxer_moderation_form?zoomed_msg=%s" % (nmb.absolute_url(),
                                                                                msg_rpath)
            nmb_mail_moderate_1 = cpsmcat('nmb_mail_moderate_1').encode('ISO-8859-15', 'ignore')
            nmb_mail_moderate_2 = cpsmcat('nmb_mail_moderate_2').encode('ISO-8859-15', 'ignore')
            subject = "[%s] %s" % (nmb.Title(), nmb_mail_moderate_1)
            body = "%s\n\n%s" % (nmb_mail_moderate_2, moderation_url)
            
            self.sendEmail(portal, from_address=getattr(portal,
                                                        'email_from_address'),
                           subject=subject,
                           body=self.textwrap(body, 72),
                           mto=filtered_emails)

    security.declarePrivate('sendEmail')
    def sendEmail(self, portal, from_address='nobody@example.com', reply_to=None,
                  subject='No subject', body='No body', content_type='text/plain',
                  charset='ISO-8859-15', mto=None):

        mailhost = getattr(portal, 'MailHost')
        if reply_to is None:
            reply_to = from_address
            
            content = """\
From: %s
Reply-To: %s
To: %s
Subject: %s
Content-Type: %s; charset=%s
Mime-Version: 1.0

%s"""
            content = content % (
                from_address, reply_to, ', '.join(mto), subject,
                content_type, charset, body)
            
            mailhost.send(content, mto=mto, mfrom=from_address,
                          subject=subject, encode='8bit')
        

InitializeClass(CPSMailBoxer)


def addCPSMailBoxer(dispatcher, id, title='', smtphost='127.0.0.1',
                    REQUEST=None, **kw):

    """Add a CPSMailBoxer."""
#    mb = CPSMailBoxer(id, title=title, description=description, mailto=mailto,\
#         moderator=moderator, moderated=moderated, archived=archived, mtahosts=mtahosts, **kw)
    mb = CPSMailBoxer(id, title)
    kw['catalog'] = 'Catalog'

    apply(mb.manage_changeProperties, (REQUEST,), kw)

    container = dispatcher.Destination()
    container._setObject(id, mb)
    mb = container._getOb(id)

    #Add box container
    mb.manage_addProduct['CPSDefault'].addBoxContainer(quiet=1)
    idbc = container.portal_boxes.getBoxContainerId(mb)
    box_container = getattr(mb,idbc)
    existing_boxes = box_container.objectIds()
    portal_types = container.portal_types

    #create boxes in box container if box is in boxes pass by factory
    boxes = ('boxertitle', 'mb_search','archive',)
    if boxes is not None:
        for box, props in [ (box, props) for (box, props) in \
                            CPSMAILBOXER_BOXES.items() \
                            if boxes and box in boxes]:
            if box in existing_boxes:
                box_container._delObject(box)
            portal_types.constructContent(props['type'], box_container, box)
            ob = box_container[box]
            ob.manage_changeProperties(**props)

    # Add a MailHost and a ZCatalog
    mb.manage_addProduct['CPSMailBoxer'].addCPSMailBoxerFolder(id='archive', title='Archive', boxes=('archive',))

    mb.manage_addProduct['ZCatalog'].manage_addZCatalog('Catalog','Catalog')

    try:
        # Here we try to add ZCTextIndex => 2.6.x

        class Extra:
            """ Just a dummy to build records for the Lexicon.
            """
            pass

        wordSplitter = Extra()
        wordSplitter.group = 'Word Splitter'
        wordSplitter.name = 'Whitespace splitter'

        caseNormalizer = Extra()
        caseNormalizer.group = 'Case Normalizer'
        caseNormalizer.name = 'Case Normalizer'

        mb.Catalog.manage_addProduct['ZCTextIndex'].manage_addLexicon(
                                                    'Lexicon', 'Lexicon',
                                                    (wordSplitter,
                                                     caseNormalizer))

        extra = Extra()
        extra.index_type = 'Okapi BM25 Rank'
        extra.lexicon_id = 'Lexicon'

        mb.Catalog.manage_addIndex('mailDate', 'DateIndex')
        mb.Catalog.addIndex('mailFrom', 'ZCTextIndex', extra)
        mb.Catalog.addIndex('mailSubject', 'ZCTextIndex', extra)
        mb.Catalog.addIndex('mailBody', 'ZCTextIndex', extra)

    except:
        # Old Zope => maybe I remove this sometimes...;)

        mb.Catalog.manage_addIndex('mailDate', 'FieldIndex')
        mb.Catalog.manage_addIndex('mailFrom', 'TextIndex')
        mb.Catalog.manage_addIndex('mailSubject', 'TextIndex')
        mb.Catalog.manage_addIndex('mailBody', 'TextIndex')

    # Add dtml-templates
    for (id, data) in MailBoxerTemplates.items():
        if id != 'index_html':     # It would override the default view
            mb.addDTMLMethod(id, file=data)

    if REQUEST is not None:
        url = dispatcher.DestinationURL()
        REQUEST.RESPONSE.redirect('%s/manage_main' % url)
