/**
 * Created by tklooju on 9/9/2016.
 */

Ext.define('Ext.overrides.grid.column.Widget', {
    override: 'Ext.grid.column.Widget',

    privates: {
        getFreeWidget: function() {
            var me = this,
                result = null;
                //result = me.freeWidgetStack ? me.freeWidgetStack.pop() : null;

            if (!result) {
                result = Ext.widget(me.widget);

                result.resolveListenerScope = me.listenerScopeFn;
                result.getWidgetRecord = me.widgetRecordDecorator;
                result.getWidgetColumn = me.widgetColumnDecorator;
                result.dataIndex = me.dataIndex;
                result.measurer = me;
                result.ownerCmp = me;
                // The ownerCmp of the widget is the column, which means it will be considered
                // as a layout child, but it isn't really, we always need the layout on the
                // component to run if asked.
                result.isLayoutChild = me.returnFalse;
            }
            return result;
        }
	}
});


//Ext.define('Ext.overrides.grid.column.Widget', {
//    override: 'Ext.grid.column.Widget',
//
//    privates: {
//
//        onItemAdd: function(records, index, items) {
//            var me = this,
//                view = me.getView(),
//                hasAttach = !!me.onWidgetAttach,
//                dataIndex = me.dataIndex,
//                isFixedSize = me.isFixedSize,
//                len = records.length, i,
//                record,
//                row,
//                cell,
//                widget,
//                el,
//                width;
//
//            // Loop through all records added, ensuring that our corresponding cell in each item
//            // has a Widget of the correct type in it, and is updated with the correct value from the record.
//            if (me.isVisible(true)) {
//                for (i = 0; i < len; i++) {
//                    record = records[i];
//                    if (record.isNonData) {
//                        continue;
//                    }
//
//                    row = view.getRowFromItem(items[i]);
//
//                    // May be a placeholder with no data row
//                    if (row) {
//                        cell = row.cells[me.getVisibleIndex()].firstChild;
//                        if (!isFixedSize && !width) {
//                            width = me.lastBox.width - parseInt(me.getCachedStyle(cell, 'padding-left'), 10) - parseInt(me.getCachedStyle(cell, 'padding-right'), 10);
//                        }
//
//                        widget = me.liveWidgets[record.internalId] = me.getFreeWidget();
//                        widget.$widgetColumn = me;
//                        widget.$widgetRecord = record;
//
//                        // Render/move a widget into the new row
//                        Ext.fly(cell).empty();
//
//                        el = widget.el || widget.element;
//                        if (el) {
//                            cell.appendChild(el.dom);
//                            if (!isFixedSize) {
//                                widget.setWidth(width);
//                            }
//                            widget.reattachToBody();
//                        } else {
//                            if (!isFixedSize) {
//                                widget.width = width;
//                            }
//                            widget.render(cell);
//                        }
//
//                        // The pair of operations below may result in a layout.
//                        // Therefore, they must be performed *AFTER* the widget has been
//                        // reattached to the cell.
//                        if (hasAttach) {
//                            Ext.callback(me.onWidgetAttach, me.scope, [me, widget, record], 0, me);
//                        }
//                        // Call the appropriate setter with this column's data field
//                        if (widget.defaultBindProperty && dataIndex) {
//                            widget.setConfig(widget.defaultBindProperty, record.get(dataIndex));
//                        }
//                    }
//                }
//            }
//        }
//        onItemUpdate: function(record, recordIndex, oldItemDom) {
//            console.info('********** [ CAUGHT onItemUpdate ] ****************************');
//            var me = this,
//                widget = me.liveWidgets[record.internalId],
//                view =   me.up('treepanel').getView(),
//                row =    view.getRowById(record.internalId),
//                cell =   row.cells[me.getVisibleIndex()].firstChild,
//                el, lastBox, width;
//
//            lastBox = me.lastBox;
//            if (lastBox && !me.isFixedSize && width === undefined) {
//                width = lastBox.width - parseInt(me.getCachedStyle(cell, 'padding-left'), 10) - parseInt(me.getCachedStyle(cell, 'padding-right'), 10);
//            }
//
//            Ext.fly(cell).empty();
//            if (el = (widget.el || widget.element)) {
//                cell.appendChild(el.dom);
//                if (!me.isFixedSize) {
//                    widget.setWidth(width);
//                }
//            } else {
//                if (!me.isFixedSize) {
//                    widget.width = width;
//                }
//                widget.render(cell);
//            }
//
//            this.updateWidget(record);
//        }
//
//    }
//});