##parameters=msg_paths=[],comment='',REQUEST=None
# $Id$

for msg_path in msg_paths:
    msg = context.restrictedTraverse(context.getBaseUrl() + msg_path)
    review_state = context.portal_workflow.getInfoFor(msg, 'review_state', 'nostate')
    if review_state == 'pending':
        context.portal_workflow.doActionFor(msg, 'publish', comment=comment)

if REQUEST is not None:
    url = "%s/cpsmailboxer_moderation_form?portal_status_message=nmb_psm_messages_published" % context.absolute_url()
    REQUEST.RESPONSE.redirect(url)
