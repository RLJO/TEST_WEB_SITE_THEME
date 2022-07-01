odoo.define('a4o_delivery_relaypoint.checkout', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var core = require('web.core');
    var concurrency = require('web.concurrency');
    var publicWidget = require('web.public.widget');
    require('website_sale_delivery.checkout');

    var _t = core._t;
    var dp = new concurrency.DropPrevious();
    var relaypoint_addresses = null;
    var relaypoint_map = null;

    publicWidget.registry.websiteSaleDelivery.include({

        //---------------------------------------------------------------------
        // Private
        //---------------------------------------------------------------------

        /**
         * @override
         * @private
         * @param {Object} result
         */
        _handleCarrierUpdateResult: function (result) {
            this._super(result);
            var $delivery_addresses_list = $('#addresses_list ul');
            var $delivery_relaypoint = $('#delivery_carrier_relaypoint');
            var $payButton = $('button[name="o_payment_submit_button"]');
            var $selected_relaypoint = $('#addresses_list input[name="delivery_address"]:checked');

            // Removing relay point address information to rebuild with new values
            $("input[id^=address_]").remove();
            $("label[for^=address_]").remove();
            $("li[id^=address_]").remove();
            $delivery_relaypoint.addClass('d-none');
            relaypoint_addresses = null;
            relaypoint_map = null;

            if (result.status === true) {
                // The carrier selected is with relaypoint
                if (result.relaypoint_delivery === true) {
                    if (result.addresses) {
                        relaypoint_addresses = result.addresses;
                        // Map
                        var container = L.DomUtil.get('relaypoint-map');
                        if(container != null){
                            container._leaflet_id = null;
                        }
                        relaypoint_map = L.map('relaypoint-map').setView([
                                relaypoint_addresses[0]['address'].latitude,
                                relaypoint_addresses[0]['address'].longitude,
                                ], 13);
                        L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
                                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                                minZoom: 1,
                                maxZoom: 20,
                                }).addTo(relaypoint_map);
                        
                        for (var index in relaypoint_addresses) {
                            var address = relaypoint_addresses[index]['address']
                            var details = [address.street, address.street2, address.zip + ' ' + address.city]
                            var id = '"address_' + index + '"'
                            var input = '<input name="delivery_address" type="radio" value=' + index + ' id=' + id + '> ';
                            var label = '<label class="label-optional" for=' + id +'> ' + address.name + '<p class="text-muted">' + details.filter(Boolean).join(', ') + '</p></label>';
                            $delivery_addresses_list.append('<li class="list-group-item" id=' + id + '>' + input + label + '</li>');
                            // add the marker to the Map:
                            var marker = L.marker([address.latitude, address.longitude]).addTo(relaypoint_map);
                            marker.bindPopup(address.name);
                            relaypoint_addresses[index]['marker'] = marker;
                        }
                        // Fix: Show all the tiles
                        setTimeout(function () {relaypoint_map.invalidateSize()}, 400);

                        if ($selected_relaypoint.val()) {
                            // If a relaypoint is selected we can activate the pay button
                            var disabledReasons = $payButton.data('disabled_reasons') || {};
                            disabledReasons.carrier_selection = false;
                            $payButton.data('disabled_reasons', disabledReasons);
                            $payButton.prop('disabled', _.contains($payButton.data('disabled_reasons'), true));
                            
                        }
                        else{
                            var disabledReasons = $payButton.data('disabled_reasons') || {};
                            disabledReasons.carrier_selection = true;
                            $payButton.data('disabled_reasons', disabledReasons);
                            $payButton.prop('disabled', _.contains($payButton.data('disabled_reasons'), true));
                        }
                        var $relaypoints = $("#delivery_carrier_relaypoint input[name='delivery_address']");
                        $relaypoints.click(this._onRelayPointClick);
                    }
                    $delivery_relaypoint.removeClass('d-none');
                }
                else {
                    // Not delivery to relaypoint ...
                    var disabledReasons = $payButton.data('disabled_reasons') || {};
                    disabledReasons.carrier_selection = false;
                    $payButton.data('disabled_reasons', disabledReasons);
                    $payButton.prop('disabled', _.contains($payButton.data('disabled_reasons'), true)); 
                }
            }
        },
        //---------------------------------------------------------------------
        // Handlers
        //---------------------------------------------------------------------

        /**
         * @private
         * @param {Event} ev
         */
        _onRelayPointClick: function (ev) {
            var idx = $(ev.currentTarget).val()
            if (idx) {
                if (relaypoint_map) {
                    // Reset the previous selected marker (if any)
                    if (relaypoint_addresses['last_marker']) {
                        relaypoint_addresses['last_marker'].valueOf()._icon.classList.remove('select_marker');
                    }
                    // Center the map to selected address
                    relaypoint_map.panTo(new L.LatLng(
                        relaypoint_addresses[idx]['address'].latitude,
                        relaypoint_addresses[idx]['address'].longitude,
                    ));
                    // Change the color of the marker
                    relaypoint_addresses[idx].marker.valueOf()._icon.classList.add("select_marker");
                    // Backup the selected marker
                    relaypoint_addresses['last_marker'] = relaypoint_addresses[idx].marker
                }
                if (relaypoint_addresses) {
                    var idx = $('#addresses_list input[name="delivery_address"]:checked').val();
                    var values = {'address': relaypoint_addresses[idx]['address']};
                    dp.add(ajax.jsonRpc('/shop/update_delivery_address', 'call', values));
                }
                // Activate the Pay button
                var $payButton = $('button[name="o_payment_submit_button"]');
                var disabledReasons = $payButton.data('disabled_reasons') || {};
                disabledReasons.carrier_selection = false;
                $payButton.data('disabled_reasons', disabledReasons);
                $payButton.prop('disabled', _.contains($payButton.data('disabled_reasons'), true));
            }
        },  
    });
});
