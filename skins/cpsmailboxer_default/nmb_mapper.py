##parameters=REQUEST=None

# $Id$

#this script is to be used in conjunction with the new tool associated
#with CPSMailBoxer called NMBMapperTool.

#Receiving a request from an SMTP server through smtp2zope, this script
#asks NMBMapperTool for the mailboxer associated with the incoming
#mail's TO address. If it finds one, it builds the appropriate HTTP
#request and redirects automatically to it, so that the message gets
#processed by the mailboxer (archiving, forwarding to members, etc.).

ntool = context.portal_mailboxermapper

mail = REQUEST.get('Mail',None)

if mail:
    recipient = ntool.getMailRecipient(mail=mail)
    mb = ntool.getMailBoxer(list=recipient)
    if mb is not None:
        mb_path = context.portal_url.getPortalPath() + '/' +\
                  context.portal_url.getRelativeUrl(mb)
        if mb_path and REQUEST is not None:
            REQUEST.RESPONSE.redirect("%s/manage_mailboxer" % (mb_path,))

