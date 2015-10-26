Ext.define('esapp.overrides.menu.Manager', {
    override: 'Ext.menu.Manager',
    register: function(menu) {
        var me = this;

        if (!me.active) {
            Ext.onReady(me.init, me);
        }

        if (menu.floating) {
            me.menus[menu.id] = menu;
            menu.on({
                beforehide: me.onBeforeHide,
                hide: me.onHide,
                beforeshow: me.onBeforeShow,
                show: me.onShow,
                scope: me
            });
        }
    }
});