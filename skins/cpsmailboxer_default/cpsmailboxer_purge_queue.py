##parameters=REQUEST=None
# $Id$

context.getContent().resetQueue()

if REQUEST is not None:
    url = "%s/cpsmailboxer_moderation_form?portal_status_message=nmb_psm_queue_purged" % context.absolute_url()
    REQUEST.RESPONSE.redirect(url)
