define(['aloha', 'aloha/plugin', 'jquery', 'jquery19', 'ui/ui', 'aloha/ephemera', 'booktype', 'aloha/engine'],
  function (Aloha, Plugin, jQuery, jQuery19, UI, Ephemera, booktype, Engine) {
    return Plugin.create('icejs', {

      initICE: function () {
          var self = this;
          var editor = jQuery('#contenteditor');
          if (editor.data('ice-initiated') === true) return;

          var tracker = new ice.InlineChangeEditor({
            element: editor[0],
            handleEvents: true,
            currentUser: {id: window.booktype.username, name: window.booktype.username},
            customDeleteHandler: function(range, direction){
              // do more research about value param for aloha methods
              // just fake it for now
              var value = '';

              // direction: left means normal delete, right means forwarddelete
              if (direction === 'left') {
                self.alohaDelete.action(value, range)
              } else {
                self.alohaForwardDelete.action(value, range);
              }
            },
            plugins: [
              'IceAddTitlePlugin',

            ]
          });

          // set attribute, so we just enable once
          editor.data('ice-initiated', true);

          // NOTE: ask if start by default
          tracker.startTracking();
      },

      init: function () {
        var self = this;
        var fake_delete = {
          action: function(value, range) {
            console.log('Deleted by icejs');
          }
        };

        // backup old delete command
        this.alohaDelete = Engine.commands.delete;
        this.alohaForwardDelete = Engine.commands.forwarddelete;

        // override default methods
        Engine.commands.delete = fake_delete;
        Engine.commands.forwarddelete = fake_delete;

        var _destroyIceTracker = function () {
          window.tracker.stopTracking();
          delete window.tracker;
        };

        // add button handler
        UI.adopt('icejs', null, {
          click: function () {
            var body = document.getElementById('contenteditor');
            if (jQuery(body).hasClass('CT-hide')) {
              jQuery(body).removeClass('CT-hide');
            } else {
              jQuery(body).addClass('CT-hide');
            }
          }
        });

        // add aloha destro
        Aloha.bind('aloha-editable-destroyed', function (e, editable) {
          _destroyIceTracker();
        });

        // bind aloha ready
        Aloha.bind('aloha-editable-activated', function (e) {
          self.initICE();
        });
      }
    });
  });