##parameters=REQUEST=None

# $Id$

fp = context.portal_url.getRelativeUrl(context)

return context.search(query={'modified_usage': 'range:min', 'portal_type': ['CPSMailArchive'], 'review_state': 'pending', 'folder_prefix': fp}, folder_prefix=fp)
