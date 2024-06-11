odoo.define('reconcile_edit_amount.ReconciliationRenderer2', function (require) {
var ReconciliationRenderer=require('account.ReconciliationRenderer');
var rpc = require('web.rpc');

ReconciliationRenderer.ManualLineRenderer.include({
 events: _.extend({}, ReconciliationRenderer.ManualLineRenderer.prototype.events || {}, {
        'keyup .o_input, .edit_amount_input': '_onStopPropagation2',
        }),

 updatePartialAmount: function(line_id, amount) {
        var $line = this.$('.mv_line[data-line-id='+line_id+']');
        $line.find('.edit_amount').addClass('d-none');
        $line.find('.edit_amount_input').removeClass('d-none');
        $line.find('.edit_amount_input').focus();
        $line.find('.edit_amount_input').val(amount);
        $line.find('.edit_amount_input').data("line_id",line_id);
        $line.find('.line_amount').addClass('d-none');
    },
  _onStopPropagation2: function(ev) {
        rpc.query({
                                model: 'account.move.line',
                                method: 'edit_reconcil_amount',
                                args: [[$(ev.target).data('line_id')],$(ev.target).val()],
                            })
        console.log("DDDL",$(ev.target))
    },
})
});

//