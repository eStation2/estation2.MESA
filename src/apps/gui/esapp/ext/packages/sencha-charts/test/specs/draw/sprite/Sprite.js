describe("Ext.draw.sprite.Sprite", function () {

    describe("isVisible", function () {
        var none = 'none',
            rgba_none = 'rgba(0,0,0,0)',
            sprite, surface, container;

        beforeEach(function () {
            container = new Ext.draw.Container({
                renderTo: Ext.getBody()
            });
            surface = new Ext.draw.Surface();
            sprite = new Ext.draw.sprite.Rect({
                hidden: false,
                globalAlpha: 1,
                fillOpacity: 1,
                strokeOpacity: 1,
                fillStyle: 'red',
                strokeStyle: 'red'
            });
            surface.add(sprite);
            container.add(surface);
        });

        afterEach(function () {
            Ext.destroy(sprite, surface, container);
        });

        it("should return true if the sprite belongs to a visible parent, false otherwise", function () {
            expect(sprite.isVisible()).toBe(true);

            surface.remove(sprite);
            expect(sprite.isVisible()).toBe(false);

            var instancing = new Ext.draw.sprite.Instancing({
                template: sprite
            });
            surface.add(instancing);
            expect(sprite.isVisible()).toBe(true);

            instancing.destroy();
        });

        it("should return false if the sprite belongs to a parent that doesn't belong to a surface", function () {
            var instancing = new Ext.draw.sprite.Instancing({
                template: sprite
            });
            expect(sprite.isVisible()).toBe(false);
        });

        it("should return false in case the sprite is hidden", function () {
            sprite.hide();
            expect(sprite.isVisible()).toBe(false);
        });

        it("should return false in case the sprite has no fillStyle and strokeStyle, true otherwise", function () {
            sprite.setAttributes({
                fillStyle: none
            });
            expect(sprite.isVisible()).toBe(true);

            sprite.setAttributes({
                fillStyle: rgba_none
            });
            expect(sprite.isVisible()).toBe(true);

            sprite.setAttributes({
                fillStyle: 'red',
                strokeStyle: none
            });
            expect(sprite.isVisible()).toBe(true);

            sprite.setAttributes({
                strokeStyle: rgba_none
            });
            expect(sprite.isVisible()).toBe(true);

            sprite.setAttributes({
                fillStyle: none,
                strokeStyle: none
            });
            expect(sprite.isVisible()).toBe(false);

            sprite.setAttributes({
                fillStyle: none,
                strokeStyle: rgba_none
            });
            expect(sprite.isVisible()).toBe(false);

            sprite.setAttributes({
                fillStyle: rgba_none,
                strokeStyle: none
            });
            expect(sprite.isVisible()).toBe(false);

            sprite.setAttributes({
                fillStyle: rgba_none,
                strokeStyle: rgba_none
            });
            expect(sprite.isVisible()).toBe(false);
        });

        it("should return false if the globalAlpha attribute is zero", function () {
            sprite.setAttributes({
                globalAlpha: 0
            });
            expect(sprite.isVisible()).toBe(false);
        });

        it("should return false if both fill and stroke are completely transparent, true otherwise", function () {
            sprite.setAttributes({
                fillOpacity: 0,
                strokeOpacity: 0
            });
            expect(sprite.isVisible()).toBe(false);

            sprite.setAttributes({
                fillOpacity: 0,
                strokeOpacity: 0.01
            });
            expect(sprite.isVisible()).toBe(true);

            sprite.setAttributes({
                fillOpacity: 0.01,
                strokeOpacity: 0
            });
            expect(sprite.isVisible()).toBe(true);
        });
    });

    describe("hitTest", function () {
        var sprite, surface, container;

        beforeEach(function () {
            container = new Ext.draw.Container({
                renderTo: Ext.getBody()
            });
            surface = new Ext.draw.Surface();
            sprite = new Ext.draw.sprite.Circle({
                hidden: false,
                globalAlpha: 1,
                fillOpacity: 1,
                strokeOpacity: 1,
                fillStyle: 'red',
                strokeStyle: 'red',
                r: 100,
                cx: 100,
                cy: 100
            });
            surface.add(sprite);
            container.add(surface);
        });

        afterEach(function () {
            Ext.destroy(sprite, surface, container);
        });

        it("should return an object with the 'sprite' property set to the sprite itself, " +
            "if the sprite is visible and its bounding box is hit", function () {
            // Testing hitTest method of the abstract Sprite class.
            // Even though, (10,10) is not inside the circle, it's inside it's bounding box.
            var result = Ext.draw.sprite.Sprite.prototype.hitTest.call(sprite, [10, 10]);
            expect(result && result.sprite).toBe(sprite);
        });

        it("should return null, if the sprite's bounding box is hit, but the sprite is not visible", function () {
            var originalMethod = sprite.isVisible;
            sprite.isVisible = function () { return false; };
            var result = Ext.draw.sprite.Sprite.prototype.hitTest.call(sprite, [10, 10]);
            expect(result).toBe(null);
            sprite.isVisible = originalMethod;
        });

        it("should return null, if the sprite is visible, but it's bounding box is not hit", function () {
            var result = Ext.draw.sprite.Sprite.prototype.hitTest.call(sprite, [210, 210]);
            expect(result).toBe(null);
        });
    });

});