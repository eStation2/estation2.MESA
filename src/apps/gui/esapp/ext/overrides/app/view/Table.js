Ext.define('esapp.overrides.view.Table', {
    override: 'Ext.view.Table',
    checkThatContextIsParentGridView: function(e){
        var target = Ext.get(e.target);
        var parentGridView = target.up('.x-grid-view');
        if (this.el != parentGridView) {
            /* this is event of different grid caused by grids nesting */
            return false;
        } else {
            var parentParentGridView = target.up().up('.x-grid-view');
            if (this.el != parentParentGridView){
                return false;
            }
            else {
                var parentParentParentGridView = target.up().up().up('.x-grid-view');
                if (this.el != parentParentParentGridView){
                    return false;
                }
                else {
                    return true;
                }
            }
        }
    },
    processItemEvent: function(record, row, rowIndex, e) {
        if (e.target && !this.checkThatContextIsParentGridView(e)) {
            return false;
        } else {
            return this.callParent([record, row, rowIndex, e]);
        }
    }
});