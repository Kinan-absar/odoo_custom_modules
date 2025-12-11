{
    'name': 'Petty Cash Management',
    'version': '1.0',
    'author': 'Kinan',
    'website': 'absar-alomran.com',
    'category': 'Accounting',
    'summary': 'Manage petty cash expenses with approval workflow and draft journal entry creation.',
    'description': """
        A custom petty cash management module that allows users to submit petty cash reports,
        attach receipts, compute VAT, categorize expenses, and generate draft accounting entries.
    """,
    'depends': ['base', 'account', 'mail', 'web'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/petty_cash_sequence.xml',
        'views/petty_cash_category_views.xml',
        'views/petty_cash_line_views.xml',
        'views/petty_cash_views.xml',     # <-- action defined here (must load first)
        'views/menus.xml',                # <-- menu referencing action (must load last)
    ],
    'images': ['static/description/icon.png'],   # <-- App icon
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
}
