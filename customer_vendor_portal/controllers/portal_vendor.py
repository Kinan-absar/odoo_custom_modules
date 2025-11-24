# -*- coding: utf-8 -*-
from odoo import http, _, fields
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class VendorPortal(CustomerPortal):

    # ---------------------------------------------------------
    # VENDOR HOME
    # ---------------------------------------------------------
    @http.route(['/vendor'], type='http', auth='public', website=True)
    def vendor_home(self, **kw):
        user = request.env.user

        if not user.partner_id.supplier_rank:
            return request.redirect('/my')  # not a vendor

        values = {
            'vendor_name': user.partner_id.name,
        }
        return request.redirect('/my/home')

    # ---------------------------------------------------------
    # PURCHASE ORDER LIST
    # ---------------------------------------------------------
    @http.route(['/vendor/pos'], type='http', auth='public', website=True)
    def vendor_po_list(self, page=1, **kw):
        user = request.env.user
        partner = user.partner_id

        if not partner.supplier_rank:
            return request.redirect('/my')

        PurchaseOrder = request.env['purchase.order']
        domain = [
            ('partner_id', '=', partner.id),
            ('state', 'in', ['purchase', 'done'])
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
    @http.route(['/vendor/po/<int:po_id>'], type='http', auth='public', website=True)
    def vendor_po_detail(self, po_id, **kw):
        user = request.env.user
        partner = user.partner_id

        po = request.env['purchase.order'].sudo().browse(po_id)

        if po.partner_id.id != partner.id or po.state not in ['purchase', 'done']:
            return request.redirect('/vendor/pos')


        values = {
            'po': po,
        }
        return request.render('customer_vendor_portal.vendor_po_detail', values)

    # ---------------------------------------------------------
    # VENDOR INVOICE LIST
    # ---------------------------------------------------------
    @http.route(['/vendor/invoices'], type='http', auth='public', website=True)
    def vendor_invoice_list(self, page=1, **kwargs):
        user = request.env.user
        partner = user.partner_id

        if not partner.supplier_rank:
            return request.redirect('/my')

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
    @http.route(['/vendor/invoice/upload'], type='http', auth='public', methods=['GET'], website=True)
    def vendor_invoice_upload_form(self, **kwargs):
        user = request.env.user
        partner = user.partner_id

        if not partner.supplier_rank:
            return request.redirect('/my')

        purchase_orders = request.env['purchase.order'].sudo().search([('partner_id', '=', partner.id)])

        values = {
            'purchase_orders': purchase_orders,
        }
        return request.render('customer_vendor_portal.vendor_invoice_upload_form', values)

    # ---------------------------------------------------------
    # SUBMIT INVOICE (POST)
    # ---------------------------------------------------------
    @http.route(['/vendor/invoice/upload'], type='http', auth='public',
                methods=['POST'], website=True, csrf=True)
    def vendor_invoice_upload(self, **post):
        import base64

        user = request.env.user
        partner = user.partner_id

        if not partner.supplier_rank:
            return request.redirect('/my')

        po_id = int(post.get('po_id') or 0)
        amount = post.get('amount_total')
        date = post.get('invoice_date')
        notes = post.get('notes')

        # HANDLE FILE UPLOAD
        file = post.get('invoice_file')
        attachment_id = False

        if file:
            file_content = file.read()

            attachment_id = request.env['ir.attachment'].sudo().create({
                'name': file.filename,
                'datas': base64.b64encode(file_content).decode(),
                'type': 'binary',
                'res_model': 'portal.vendor.invoice',
                'res_id': 0,
            }).id

        request.env['portal.vendor.invoice'].sudo().create({
            'partner_id': partner.id,
            'po_id': po_id,
            'amount_total': amount,
            'invoice_date': date,
            'notes': notes,
            'attachment_id': attachment_id,
            'portal_user_id': user.id,
            'vendor_invoice_number': post.get('vendor_invoice_number'),
        })

        return request.redirect('/vendor/invoices?submitted=1')

