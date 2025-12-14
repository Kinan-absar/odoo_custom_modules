# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class VendorPortal(CustomerPortal):

    # ---------------------------------------------------------
    # VENDOR ENTRY POINT
    # ---------------------------------------------------------
    @http.route(['/vendor'], type='http', auth='user', website=True)
    def vendor_home(self, **kw):
        user = request.env.user

        # Not a vendor → normal portal home
        if not user.partner_id.supplier_rank:
            return request.redirect('/my/home')

        # Vendor → portal home (dashboard)
        return request.redirect('/my/home')

    # ---------------------------------------------------------
    # PURCHASE ORDER LIST
    # ---------------------------------------------------------
    @http.route(['/vendor/pos'], type='http', auth='user', website=True)
    def vendor_po_list(self, page=1, **kw):
        user = request.env.user
        partner = user.partner_id

        if not partner.supplier_rank:
            return request.redirect('/my/home')

        PurchaseOrder = request.env['purchase.order']
        domain = [
            ('partner_id', '=', partner.id),
            ('state', 'in', ['purchase', 'done']),
        ]

        pos_count = PurchaseOrder.search_count(domain)
        pager = portal_pager(
            url='/vendor/pos',
            total=pos_count,
            page=page,
            step=10
        )

        pos = PurchaseOrder.search(domain, limit=10, offset=pager['offset'])

        values = {
            'pos': pos,
            'pager': pager,
        }
        return request.render('customer_vendor_portal.vendor_po_list', values)

    # ---------------------------------------------------------
    # PURCHASE ORDER DETAIL
    # ---------------------------------------------------------
    @http.route(['/vendor/po/<int:po_id>'], type='http', auth='user', website=True)
    def vendor_po_detail(self, po_id, **kw):
        user = request.env.user
        partner = user.partner_id

        po = request.env['purchase.order'].sudo().browse(po_id)

        if po.partner_id.id != partner.id or po.state not in ['purchase', 'done']:
            return request.redirect('/vendor/pos')

        return request.render(
            'customer_vendor_portal.vendor_po_detail',
            {'po': po}
        )

    # ---------------------------------------------------------
    # VENDOR INVOICE LIST
    # ---------------------------------------------------------
    @http.route(['/vendor/invoices'], type='http', auth='user', website=True)
    def vendor_invoice_list(self, page=1, **kwargs):
        user = request.env.user
        partner = user.partner_id

        if not partner.supplier_rank:
            return request.redirect('/my/home')

        Invoice = request.env['portal.vendor.invoice']
        domain = [('partner_id', '=', partner.id)]

        invoice_count = Invoice.search_count(domain)
        pager = portal_pager(
            url='/vendor/invoices',
            total=invoice_count,
            page=page,
            step=10
        )

        invoices = Invoice.search(domain, limit=10, offset=pager['offset'])

        values = {
            'invoices': invoices,
            'pager': pager,
        }
        return request.render('customer_vendor_portal.vendor_invoice_list', values)

    # ---------------------------------------------------------
    # UPLOAD VENDOR INVOICE (FORM)
    # ---------------------------------------------------------
    @http.route(['/vendor/invoice/upload'], type='http', auth='user', methods=['GET'], website=True)
    def vendor_invoice_upload_form(self, **kwargs):
        user = request.env.user
        partner = user.partner_id

        if not partner.supplier_rank:
            return request.redirect('/my/home')

        purchase_orders = request.env['purchase.order'].sudo().search([
            ('partner_id', '=', partner.id)
        ])

        return request.render(
            'customer_vendor_portal.vendor_invoice_upload_form',
            {'purchase_orders': purchase_orders}
        )

    # ---------------------------------------------------------
    # SUBMIT INVOICE (POST)
    # ---------------------------------------------------------
    @http.route(['/vendor/invoice/upload'], type='http', auth='user',
                methods=['POST'], website=True, csrf=True)
    def vendor_invoice_upload(self, **post):
        import base64

        user = request.env.user
        partner = user.partner_id

        if not partner.supplier_rank:
            return request.redirect('/my/home')

        po_id = int(post.get('po_id') or 0)

        file = post.get('invoice_file')
        attachment_id = False

        if file:
            attachment_id = request.env['ir.attachment'].sudo().create({
                'name': file.filename,
                'datas': base64.b64encode(file.read()).decode(),
                'type': 'binary',
                'res_model': 'portal.vendor.invoice',
                'res_id': 0,
            }).id

        request.env['portal.vendor.invoice'].sudo().create({
            'partner_id': partner.id,
            'po_id': po_id,
            'amount_total': post.get('amount_total'),
            'invoice_date': post.get('invoice_date'),
            'notes': post.get('notes'),
            'attachment_id': attachment_id,
            'portal_user_id': user.id,
            'vendor_invoice_number': post.get('vendor_invoice_number'),
        })

        # ✅ After save → vendor invoice list (safe)
        return request.redirect('/vendor/invoices?submitted=1')
    # ---------------------------------------------------------
    # VENDOR DETAILS (EDIT INFORMATION)
    # ---------------------------------------------------------
    @http.route('/my/vendor/details', type='http', auth='user', website=True)
    def vendor_details(self, **post):
        partner = request.env.user.partner_id

        # POST → save changes
        if request.httprequest.method == 'POST':
            partner.sudo().write({
                'name': post.get('name'),
                'email': post.get('email'),
                'phone': post.get('phone'),
                'street': post.get('street'),
                'street2': post.get('street2'),
                'city': post.get('city'),
                'zip': post.get('zip'),
                'country_id': int(post.get('country_id')) if post.get('country_id') else False,
                'state_id': int(post.get('state_id')) if post.get('state_id') else False,
                'vat': post.get('vat'),
            })

            # ✅ AFTER SAVE → ALWAYS GO HOME
            return request.redirect('/my/home')

        # GET → show Odoo's standard details form
        return request.render(
            'portal.portal_my_details',
            {}
        )
    # ---------------------------------------------------------
    # FIX CORE PORTAL "EDIT INFORMATION" ROUTE
    # ---------------------------------------------------------
    @http.route('/my/account', type='http', auth='user', website=True)
    def portal_my_account_redirect(self, **kw):
        # Always redirect to vendor details page
        return request.redirect('/my/vendor/details')

