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
    recipient_list = ntool.getMailRecipient(mail=mail)
    for recipient in recipient_list:
        mb = ntool.getMailBoxer(list=recipient)
        if mb is not None:
            return mb.manage_mailboxer(REQUEST)
        else:
            from zLOG import LOG, INFO
            LOG("CPSMailBoxer nmb_mapper", INFO, 
                "Recipient "+str(recipient)+"has no MailBoxer")
            LOG("CPSMailBoxer nmb_mapper", INFO, 
                "Senders "+str(ntool.getMailSender(mail=mail)))
            return "FALSE"

