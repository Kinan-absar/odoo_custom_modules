{
    'name': 'ABSAR Send to Sign for Purchase Orders',
    'version': '1.0.0',
    'summary': 'Director → CEO digital signing workflow for purchase orders using Odoo Sign.',
    'author': 'Kinan',
    'website': 'https://absar-alomran.com',
    'category': 'Purchases',
    'depends': ['purchase', 'sign', 'mail'],
    'data': [
        'views/purchase_order_view.xml',
        'views/res_company_view.xml',
        'data/cron.xml',
    ],
    'installable': True,
    'application': False,
}
