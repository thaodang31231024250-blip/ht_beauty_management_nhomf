{
    'name': 'HT Beauty Website',
    'version': '1.0',
    'category': 'HT Beauty',
    'summary': 'Tích hợp Website HT Beauty và Form liên hệ đẩy Leads về CRM',
    'author': 'Nhóm F',
    'depends': [
        'base',
        'website',
        'crm',
        'product',
        'sale_management',
        ],
    'data': [
        'security/ir.model.access.csv',
        'views/website_templates.xml',
        'data/website_menu_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'license': 'LGPL-3',
}