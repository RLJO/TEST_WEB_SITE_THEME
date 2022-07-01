# This file is part of an Adiczion's Module.
# The COPYRIGHT and LICENSE files at the top level of this repository
# contains the full copyright notices and license terms.
from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale_delivery.controllers.main import (
    WebsiteSaleDelivery)
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):

    def _get_mandatory_shipping_fields(self):
        return super()._get_mandatory_shipping_fields() + ["zip"]
    
    def _get_mandatory_billing_fields(self):
        return super()._get_mandatory_billing_fields() + ["zip"]


class WebsiteSaleDelivery(WebsiteSaleDelivery):

    def _update_website_sale_delivery_return(self, order, **post):
        result = super()._update_website_sale_delivery_return(order, **post)
        if result:
            carrier = order.carrier_id
            weight = 0.0
            for line in order.order_line:
                if not line.product_id:
                    continue
                qty = line.product_uom._compute_quantity(
                    line.product_uom_qty, line.product_id.uom_id)
                weight += (line.product_id.weight or 0.0) * qty
            addresses = None
            relaypoint_delivery = carrier.relaypoint_delivery or None
            if relaypoint_delivery:
                addresses = carrier.select_relaypoint(**{
                        'partner': order.partner_shipping_id,
                        'weight': weight,
                        })
            result.update({
                'relaypoint_delivery': relaypoint_delivery,
                'addresses': addresses,
                })
        return result

    # def _update_website_sale_delivery_address_return(self, order, **post):
    #     results = {}
    #     return results

    def _update_website_sale_delivery_address(self, **post):
        order = request.website.sale_get_order()
        address = post.get('address')
        if order and address:
            address_id = order.carrier_id.add_address(
                order.partner_shipping_id, address)
            if not address_id:
                raise Exception(_('Unable to get the relaypoint address!'
                                  ' Please contact the webmaster!'))
            values = {'partner_shipping_id': address_id.id}
            if not order.partner_shipping_id.code_relaypoint:
                values.update({
                    'original_partner_shipping_id': (
                        order.partner_shipping_id.id),
                    })
            order.write(values)
        return {}

    @http.route(['/shop/update_delivery_address'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def update_website_sale_delivery_address(self, **post):
        results = {}
        if hasattr(self, '_update_website_sale_delivery_address'):
            results.update(self._update_website_sale_delivery_address(**post))
        return results
