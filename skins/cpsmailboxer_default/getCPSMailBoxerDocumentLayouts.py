##parameters=
"""
SUEZ Layout CPS Mail Archive definition
"""

cps_mailarchive_layout = {
    'widgets': {
        'mailFrom': {
            'type': 'String Widget',
            'data': {
                'fields': ['mailFrom'],
                'is_required': 0,
                'label': 'nmb_label_mail_from',
                'label_edit': 'nmb_label_mail_from',
                'is_i18n': 1,
                'readonly_layout_modes': ['view', 'edit'],
                'hidden_layout_modes': [],
                'hidden_readonly_layout_modes': [],
                'hidden_empty': 0,
                'display_width': 20,
                'size_max': 0,
            },
        },
        'mailSubject': {
            'type': 'String Widget',
            'data': {
                'fields': ['mailSubject'],
                'is_required': 0,
                'label': 'nmb_label_mail_subject',
                'label_edit': 'nmb_label_mail_subject',
                'is_i18n': 1,
                'readonly_layout_modes': ['view', 'edit'],
                'hidden_layout_modes': [],
                'hidden_readonly_layout_modes': [],
                'hidden_empty': 0,
                'display_width': 20,
                'size_max': 0,
            },
        },
        'mailDate': {
            'type': 'DateTime Widget',
            'data': {
                'fields': ['mailDate'],
                'is_required': 0,
                'label': 'nmb_label_mail_date',
                'label_edit': 'nmb_label_mail_date',
                'is_i18n': 1,
                'readonly_layout_modes': ['view', 'edit'],
                'hidden_layout_modes': [],
                'hidden_readonly_layout_modes': [],
                'hidden_empty': 0,
                'view_format': 'medium',
                'time_setting': 1,
            },
        },
        'mailBody': {
            'type': 'Text Widget',
            'data': {
                'fields': ['mailBody'],
                'is_required': 0,
                'label': 'nmb_label_mail_body',
                'label_edit': 'nmb_label_mail_body',
                'is_i18n': 1,
                'readonly_layout_modes': ['edit', 'view'],
                'hidden_layout_modes': [],
                'hidden_readonly_layout_modes': [],
                'hidden_empty': 0,
                'width': 40,
                'height': 5,
                'size_max': 0,
                'render_position': 'normal',
                'render_format': 'text',
                'configurable': 'nothing',
            },
        },
        'Mailattachment': {
            'type': 'AttachedFile Widget',
            'data': {
                'fields': ['?'],
                'is_required': 0,
                'label': 'nmb_label_mail_attachment',
                'label_edit': 'nmb_label_mail_attachment',
                'is_i18n': 1,
                'readonly_layout_modes': [],
                'hidden_layout_modes': [],
                'hidden_readonly_layout_modes': [],
                'hidden_empty': 0,
                'deletable': 1,
                'size_max': 4194304,
            },
        },
    },
    'layout': {
        'style_prefix': 'layout_default_',
        'flexible_widgets': ['Mailattachment'],
        'ncols': 1,
        'rows': [
            [{'ncols': 1, 'widget_id': 'mailFrom'},
            ],
            [{'ncols': 1, 'widget_id': 'mailSubject'},
            ],
            [{'ncols': 1, 'widget_id': 'mailDate'},
            ],
            [{'ncols': 1, 'widget_id': 'mailBody'},
            ],
        ],
    },
}

cps_mailarchive_flexible_layout = {
    'widgets': {
        'Mailattachment': {
            'type': 'File Widget',
            'data': {
                'fields': ['?'],
                'is_required': 0,
                'label': 'nmb_label_mail_attachment',
                'label_edit': 'nmb_label_mail_attachment',
                'is_i18n': 1,
                'readonly_layout_modes': [],
                'hidden_layout_modes': [],
                'hidden_readonly_layout_modes': [],
                'hidden_empty': 0,
                'hidden_if_expr': '',
                'css_class': '',
                'deletable': 1,
                'size_max': 4194304,
            },
        },
    },
    'layout': {
        'style_prefix': 'layout_default_',
        'flexible_widgets': ['Mailattachment'],
        'ncols': 1,
        'rows': [
        ],
    },
}

layouts = {}

layouts['cps_mailarchive'] = cps_mailarchive_layout
layouts['cps_mailarchive_flexible'] = cps_mailarchive_flexible_layout

return layouts
