##parameters=
#$Id$
"""
CPSMailBoxer archives stored as CPSDocument
"""

mailarchive_type = {
    'title': 'CPSMailArchive_title',
    'description': 'CPSMailArchive_description',
    'content_icon': 'MailHost_icon.gif',
    'content_meta_type': 'CPSMailArchive',
    'product': 'CPSMailBoxer',
    'factory': 'addInstance',
    'immediate_view': '',
    'global_allow': 1,
    'filter_content_types': 1,
    'allowed_content_types': [],
    'allow_discussion': 0,
    'cps_is_searchable': 1,
    'cps_proxy_type': 'document',
    'cps_display_as_document_in_listing': 1,
    'schemas': ['common', 'metadata', 'cps_mailarchive', 'cps_mailarchive_flexible'],
    'layouts': ['common', 'cps_mailarchive', 'cps_mailarchive_flexible'],
    'flexible_layouts': ['cps_mailarchive_flexible:cps_mailarchive_flexible'],
    'storage_methods': [],
    }


return {
    'CPSMailArchive': mailarchive_type,
    }
