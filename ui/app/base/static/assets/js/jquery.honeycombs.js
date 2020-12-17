(function($) {

    $.fn.honeycombs = function(options) {

        // Establish our default settings
        var settings = $.extend({
            combWidth: 250,
            margin: 0,
            threshold: 3
        }, options);

        function initialise(element) {

            $(element).addClass('honeycombs-wrapper');

            var width = 0;
            var combWidth = 0;
            var combHeight = 0;
            var num = 0;
            var $wrapper = null;

            /**
             * Build the dom
             */
            function buildHtml(){
                // add the 2 other boxes
                $(element).find('.comb').wrapAll('<div class="honeycombs-inner-wrapper"></div>');
                $wrapper = $(element).find('.honeycombs-inner-wrapper');

                $(element).find('.comb').append('<div class="inner front"></div>');
                $(element).find('.comb').append('<div class="inner back"></div>');
                $(element).find('.inner').append('<div class="wrapper"></div>');
                $(element).find('.comb').append('<span class="icon-hex-lg"></span>');

                num = 0;

                $(element).find('.comb').each(function(){
                    num = num + 1;

                    if($(this).find('.inner').length > 0){
                        $(this).find('.inner.front .wrapper').html($(this).find('.front-content').html());
                        $(this).find('.inner.back .wrapper').html($(this).find('.back-content').html());
                        $(this).find('.front-content').remove();
                        $(this).find('.back-content').remove();
                    }else{
                        $(this).find('.inner').remove();
                    };
                });

                // Fix Firefox padding error
                /*ccamacho: FIXME: adding the firefox class breaks the hexagon render*/
                /*
                if (navigator.userAgent.search("Firefox") > -1) {
                    $('.comb span').addClass('firefox');
                }
                */
            }

            /**
             * Update all scale values
             */
            function updateScales(){
                combWidth = settings.combWidth;
                combHeight = combWidth;
                $(element).find('.comb').width(combWidth).height(combHeight);
                $(element).find('.icon-hex-lg').css('font-size', combWidth)
            }

            /**
             * update css classes
             */
            function reorder(animate){

                updateScales();
                width = $(element).width();

                newWidth = $('.honeycombs').parent().width();


                if(newWidth < width){
                    width = newWidth;
                }

                $wrapper.width(newWidth);

                var maxLeft = 0;
                var row = 0; // current row
                var offset = 0; // 1 is down
                var left = 1; // pos left
                var top = 0; // pos top
                var cols = 0;

                var noOffset = function(offset){
                    return offset
                };

                var withOffset = function(offset){
                    return (offset + 1) % 2;
                }

                var halfTop = function(top){
                    return ( row * ( 0.5 * combHeight * Math.sqrt(3) + settings.margin) )
                }

                var fullTop = function(top){
                    return ( row * (combHeight + settings.margin + combHeight * 0.1))
                }

                function orderCombs(leftHandler, topHandler){

                    $(element).find('.comb').filter(':not(.placeholder.hide)').each(function(index){

                        top = topHandler(top);

                        if(animate == true){
                            $(this).stop(true, false);
                            $(this).animate({'left': left, 'top': top});
                        }else{
                            $(this).css('left', left).css('top', top);
                        }

                        left = left + ( combWidth + settings.margin );

                        if(left > maxLeft) {
                            maxLeft = left;
                        }


                        if(row == 0){
                            cols = cols + 1;
                        }

                        if(left + combWidth > width){
                            row = row + 1;
                            offset = leftHandler(offset);
                            left = offset / 2 * ( combWidth + settings.margin ) ;
                        }

                    });
                }


                if (newWidth < 1.5 * (combWidth + settings.margin)) {
                    $('.comb.placeholder').addClass('hide');

                    orderCombs(noOffset, fullTop);
                } else if (newWidth < settings.threshold * (combWidth + settings.margin)) {
                    $('.comb.placeholder').addClass('hide');
                    orderCombs(withOffset, halfTop);
                } else {
                    $('.comb.placeholder').removeClass('hide');
                    orderCombs(withOffset, halfTop);
                }


                $wrapper
                    .height(top + combHeight)
                    .width(maxLeft - settings.margin)
            }

            $(window).resize(function(){
                reorder(true);
            });

            buildHtml();
            reorder(false);
        }

        return this.each(function() {
            initialise(this);
        });

    }

}(jQuery));
