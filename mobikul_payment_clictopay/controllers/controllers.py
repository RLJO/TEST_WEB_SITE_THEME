# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

import logging
_logger = logging.getLogger(__name__)
from odoo import http
from odoo.tools.translate import _
from odoo.http import request
from odoo.addons.mobikul.controllers.main import WebServices
import requests
from ast import literal_eval
import json
from odoo import api, fields
import werkzeug.utils
from werkzeug.exceptions import BadRequest
from odoo.service import common
from urllib.parse import urlencode
from odoo.addons.payment_clictopay.models.currency import CURRENCY_CODE


class WebServices(WebServices):

    def _getAquirerCredentials(self, order_name, Acquirer, txn, response):
        if Acquirer.mobikul_reference_code == 'CLICTOPAY':
            currency = txn.currency_id.name
            merchant_detail = request.env["payment.acquirer"].sudo().browse(Acquirer.id)
            order = txn.partner_id.last_mobikul_so_id
            total_amount = order.amount_total
            base_url = request.httprequest.host_url
            request.context = dict(request.context,reference=txn.reference)
            clictopay_tx_values = {
                'userName': merchant_detail.detail_clictopay_payment_acquire().get('Username'),
                'password': merchant_detail.detail_clictopay_payment_acquire().get('Password'),
                'returnUrl': base_url+'app/clictopay/feedback',
                'orderNumber': txn.reference,
                'currency': int(CURRENCY_CODE.get(currency)),
                'amount': int(total_amount*1000),
                'pageView':'DESKTOP',

                }
            url = merchant_detail.clictopay_url().get('pay_page_url')+"?"+urlencode(clictopay_tx_values)
            result = requests.post(url= url)
            request_params = literal_eval(result.text)
            if request_params.get("orderId") and request_params.get("formUrl"):
                return {'status':True,'paymentUrl':request_params.get("formUrl"),'code':'CLICTOPAY','auth':True,"acquire":Acquirer.name}
            else:
                return {'status':False,'code':'CLICTOPAY','acquire':Acquirer.name,'error_message':request_params.get("errorMessage")}
        else :
            result =  super(WebServices,self)._getAquirerCredentials(order_name=order_name, Acquirer=Acquirer,txn=txn,response=response)
            return result


    _app_return_url = '/app/clictopay/feedback'

    @http.route([_app_return_url], type='http',csrf=False, auth='public', website=True)
    def app_clictopay_feedback(self, **post):
        merchant_detail = request.env["payment.acquirer"].sudo().search([("provider","=","clictopay")])
        try:
            params = {
                'userName': merchant_detail.detail_clictopay_payment_acquire().get('Username'),
                'password': merchant_detail.detail_clictopay_payment_acquire().get('Password'),
                'orderId': post.get('orderId')
                }
            url = str(merchant_detail.clictopay_url().get("order_status"))+"?"+ urlencode(params)
            result = requests.get(url=url)
            request_params = json.loads(result.text)

        except Exception as e:
            request_params = {
            'status':'cancel',
            "reference_no": request.context.get('reference'),
            'result': 'The payment is cancelled successfully!',
            'response_code': '403'
            }
        txn  = request.env['payment.transaction'].sudo()
        txn.form_feedback(request_params, 'clictopay')
        txnObj = txn.search([('reference', '=',request_params.get('OrderNumber'))])
        status = self.check_status(txnObj)
        return werkzeug.utils.redirect('/app/payment/clicktopay/result?%s'%urlencode(status))

    def check_status(self,txnObj):
        status = {}
        if txnObj.state == "pending":
            status["status"] = "pending"
        elif txnObj.state == "done":
            status["status"] = "success"
        elif txnObj.state == "error":
            status["status"] = "error"
        elif txnObj.state == "cancel":
            status["status"] = "cancel"
        return status

    @http.route(['/app/payment/clicktopay/result',], type='http', auth="public", website=True)
    def app_payment_clictopay_result(self, **kw):
        return request.render("mobikul_payment_clictopay.result_id")
