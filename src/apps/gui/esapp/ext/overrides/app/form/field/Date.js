/**
 * Created by tklooju on 10/14/2015.
 */
Ext.define('esapp.overrides.picker.Date', {
    override: 'Ext.picker.Date',


    runAnimation: function(isHide) {
        var me = this,
            picker = this.monthPicker,
            options = {
                duration: 200,
                callback: function() {
                    picker.setVisible(!isHide);
                    // See showMonthPicker
                    picker.ownerCmp = isHide ? null : me;
                }
            };


        if (isHide) {
            picker.el.slideOut('t', options);
        } else {
            picker.el.slideIn('t', options);
        }
    },


    hideMonthPicker: function(animate) {
        var me = this,
            picker = me.monthPicker;


        if (picker && picker.isVisible()) {
            if (me.shouldAnimate(animate)) {
                me.runAnimation(true);
            } else {
                picker.hide();
                // See showMonthPicker
                picker.ownerCmp = null;
            }
        }
        return me;
    },


    showMonthPicker: function(animate) {
        var me = this,
            el = me.el,
            picker;


        if (me.rendered && !me.disabled) {
            picker = me.createMonthPicker();
            if (!picker.isVisible()) {
                picker.setValue(me.getActive());
                picker.setSize(el.getSize());
                picker.setPosition(-el.getBorderWidth('l'), -el.getBorderWidth('t'));
                if (me.shouldAnimate(animate)) {
                    me.runAnimation(false);
                } else {
                    picker.show();
                    // We need to set the ownerCmp so that owns() can correctly
                    // match up the component hierarchy, however when positioning the picker
                    // we don't want it to position like a normal floater because we render it to
                    // month picker element itself.
                    picker.ownerCmp = me;
                }
            }
        }
        return me;
    }
});