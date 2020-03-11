Ext.define('Ext.overrides.grid.NavigationModel', {
   override: 'Ext.grid.NavigationModel',

   onCellMouseDown: function(view, cell, cellIndex, record, row, recordIndex, mousedownEvent) {
      var targetComponent = Ext.Component.fromElement(mousedownEvent.target, cell),
         ac;

      if (view.actionableMode && (mousedownEvent.getTarget(null, null, true).isTabbable() || ((ac = Ext.ComponentManager.getActiveComponent()) && ac.owns(mousedownEvent)))) {
         return;
      }

      if (mousedownEvent.pointerType !== 'touch') {
         // mousedownEvent.preventDefault(); // commented for text selection
         this.setPosition(mousedownEvent.position, null, mousedownEvent);
      }

      if (targetComponent && targetComponent.isFocusable && targetComponent.isFocusable()) {
         view.setActionableMode(true, mousedownEvent.position);

         targetComponent.focus();
      }
   }
});