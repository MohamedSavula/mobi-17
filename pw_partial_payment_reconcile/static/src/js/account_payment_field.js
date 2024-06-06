/** @odoo-module */
import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

import { AccountPaymentField } from "@account/components/account_payment_field/account_payment_field";

patch(AccountPaymentField.prototype, {
    setup(attributes) {
        super.setup(...arguments);
    },
    async partialOutstandingCredit(move_id, line_id) {
        this.action.doAction({
            name: 'Partial Payment Recocile',
            type: 'ir.actions.act_window',
            res_model: 'partial.payment.wizard',
            views: [[false, 'form']],
            target: 'new',
            context: {'line_id': line_id, 'move_id': move_id},
        });
    }
});
