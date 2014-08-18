// from http://stackoverflow.com/questions/9235304/how-to-replace-the-location-hash-and-only-keep-the-last-history-entry
(function(namespace) { // Closure to protect local variable "var hash"
    if ('replaceState' in history) { // Yay, supported!
        namespace.replaceHash = function(newhash) {
            if ((''+newhash).charAt(0) !== '#') newhash = '#' + newhash;
            history.replaceState('', '', newhash);
        }
    } else {
        var hash = location.hash;
        namespace.replaceHash = function(newhash) {
            if (location.hash !== hash) history.back();
            location.hash = newhash;
        };
    }
})(window);

(function($) {
    var stylesXHR = $.getJSON('assets/styles.json');
    var dataXHR = $.getJSON('assets/tree.json');

    $.when(stylesXHR, dataXHR).done(function(stylesResult, dataResult) {
        styles = stylesResult[0];
        data = dataResult[0];

        var $svg = $('svg');

        var margin = 20,
            width = $svg.width(),
            height = $svg.height();

        var diameter = Math.min(height, width);

        var color = d3.scale.linear()
            .domain([1, 3])
            .range([styles.colors.data.main.yellow.subsets[0].hex, styles.colors.data.main.yellow.subsets[1].hex])
            .interpolate(d3.interpolateHcl);

        var pack = d3.layout.pack()
            .padding(2)
            .size([width, height])
            .value(function(d) { return d.size; })

        var svg = d3.select($svg[0])
            .append("g")
                .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")")
                .attr('class', 'main');

        var annotations = d3.select($svg[0])
            .append("g");

        var root = {'children': data, 'size': $.map(data, function(el) { return el.size; }).reduce(function(a, b) { return a + b; }, 0)};

        var focus = root,
            nodes = pack.nodes(root),
            view;

        var shadow = '0 1px 0 rgba(255,255,255,0.25), 1px 0 0 rgba(255,255,255,0.25), -1px 0 0 rgba(255,255,255,0.25), 0 -1px 0 rgba(255,255,255,0.25)';
        //var shadow = '';

        var circle = svg.selectAll("circle")
            .data(nodes)
          .enter().append("circle")
            .attr('id', function(d) { return d.id ? 'circle-' + d.id : null; })
            .attr("class", function(d) { return d.parent ? d.children ? "node" : "node node--leaf" : "node node--root"; })
            .style("fill", function(d) { return d.parent ? color(d.depth) : "none"; })
            .style("pointer-events", function(d) { return d.parent ? "auto" : "none"})
            .on("click", function(d) { if (focus !== d) zoom(d), d3.event.stopPropagation(); });

        var text = svg.selectAll("text")
            .data(nodes)
            .enter()
                .append("g")
                    .attr("class", "label-group")
                    .each(function(d, i) {
                        d3.select(this)
                            .append("text")
                            .attr("class", "label")
                            .style("fill-opacity", function(d) { return d.parent === root ? 1 : 0; })
                            .style("display", function(d) { return d.parent === root ? "inline" : "none"; })
                            .style('pointer-events', 'none')
                            .style('text-anchor', 'middle')
                            .style('text-shadow', shadow)
                            .text(function(d) { return d.keywords ? d.keywords.slice(0,3).join(", ") : ""; })
                            .attr('fill', '#333');
                        d3.select(this)
                            .append("text")
                            .attr("class", "label")
                            .style("fill-opacity", function(d) { return d.parent === root ? 1 : 0; })
                            .style("display", function(d) { return d.parent === root ? "inline" : "none"; })
                            .style('pointer-events', 'none')
                            .style('text-anchor', 'middle')
                            .style('text-shadow', shadow)
                            .attr('y', 12)
                            .text(function(d) { return d.keywords ? d.keywords.slice(3,5).join(", ") : ""; })
                            .attr('fill', '#333');
                    })


        /* titles and annotations */
        var title = annotations.append("text")
            .text("")
            .style("display", "none")
            .style("font-size", "200%")
            .style('text-shadow', shadow)
            .attr('x', '20')
            .attr('y', '35')
            .attr('fill', '#333');

        var stats = annotations.append("text")
            .text("")
            .style("font-size", "150%")
            .style('text-shadow', shadow)
            .attr('x', '20')
            .attr('y', height - 20)
            .attr('fill', '#333');

        var viewButtonArea = annotations.append("foreignObject")
            .style("display", "none")
            .attr("width", 200)
            .attr("height", 100);
        viewButtonArea
            .append("xhtml:div")
            .html('<button class="btn-sunlight"><i class="glyphicon glyphicon-list-alt"></i> view</button>');
        var viewButton = viewButtonArea.selectAll('button');


        var node = svg.selectAll("circle,text");

        d3.select($svg[0])
            .on("click", function() { zoom(root); });

        zoomTo([root.x, root.y, root.r * 2 + margin]);
        updateCount(root);

        /* response to interactivity in the graph */
        var view_d = null;
        function updateCount (d) {
            stats.text(d.size + " documents (" + (100 * d.size / root.size) + "%)");
            if (d.size <= 100) {
                view_d = d;
                var box = stats.node().getBBox();
                viewButtonArea
                    .attr('x', 20 + box.width)
                    .attr('y', height - 25 - box.height)
                    .style('display', null);
            } else {
                viewButtonArea
                    .style('display', 'none');
            }
        }

        function zoom(d) {
            var focus0 = focus; focus = d;

            d3.selectAll('circle').classed('selected', false);
            if (focus.parent) {
                title
                    .style('display', 'inline')
                    .text(focus.keywords.join(", "));
                d3.selectAll('circle#circle-' + d.id).classed('selected', true);
                window.replaceHash(d.id);
            } else {
                title.style('display', 'none');
                window.replaceHash("");
            }

            updateCount(d);

            var transition = d3.transition()
                .duration(750)
                .tween("zoom", function(d) {
                  var i = d3.interpolateZoom(view, [focus.x, focus.y, focus.r * 2 + margin]);
                  return function(t) { zoomTo(i(t)); };
                });

            transition.selectAll(".main text")
              .filter(function(d) { return d.parent === focus || (d == focus && (!d.children)) || this.style.display === "inline"; })
                .style("fill-opacity", function(d) { return (d.parent === focus || (d == focus && (!d.children))) ? 1 : 0; })
                .each("start", function(d) { if (d.parent === focus || (d == focus && (!d.children))) this.style.display = "inline"; })
                .each("end", function(d) { if (d.parent !== focus && !(d.parent === focus || (d == focus && (!d.children)))) this.style.display = "none"; });
        }

        function zoomTo(v) {
            var k = diameter / v[2]; view = v;
            node.attr("transform", function(d) { return "translate(" + (d.x - v[0]) * k + "," + (d.y - v[1]) * k + ")"; });
            circle.attr("r", function(d) { return d.r * k; });
        }

        /* things to do with the dialog */
        $(viewButton[0]).on('click', function(evt) {
            evt.stopPropagation();
            evt.preventDefault();

            var dialog = $('#doc-dialog');
            dialog.modal('toggle');

           window.replaceHash(focus.id + "/docs");

            var group = dialog.find('.list-group').css('height', (height - 120) + 'px');

            var shifter = dialog.find('.panel-shifter-inner');
            if (shifter.css('position') == 'absolute') {
                // it's been animated, so un-animate it if necessary
                shifter.css('left', '0px');
            }

            group.html();
            if (view_d) {
                group.addClass('loading');
                $.getJSON("tree_data/" + view_d.id + ".json", function(tree_data) {
                    group.removeClass('loading');
                    group.html(
                        $.map(tree_data.items, function(item) { return '<a data-item-id="' + item.id + '"" href="#' + item.id + '" class="list-group-item">' + item.title + '<i class="glyphicon glyphicon-chevron-right pull-right"></i></a>' }).join("")
                    );
                });
            }
        });
        $('#doc-dialog').on('hidden.bs.modal', function () {
            window.replaceHash(focus.id);
        });

        var fixed_width = null;
        var fixed_height = null;
        $('#doc-dialog .doc-list').on('click', 'a', function(evt) {
            evt.stopPropagation();
            evt.preventDefault();

            var id = $(evt.target).attr('data-item-id');
            window.replaceHash(focus.id + "/docs/" + id);

            var outer = $('.panel-shifter-outer');
            var inner = outer.find('.panel-shifter-inner');
            var dlp = inner.find('.doc-list-panel');
            var dvp = inner.find('.doc-view-panel');

            if (!fixed_width) {
                fixed_width = dlp.width();
                fixed_height = dlp.height();
            }

            outer.css({
                'height': fixed_height + 'px',
                'width': fixed_width + 'px',
                'position': 'relative',
                'overflow': 'hidden'
            });
            inner.css({
                'position': 'absolute',
                'top': '0px',
                'left': '0px'
            });

            dlp.css({
                'position': 'absolute',
                'left': '0px',
                'height': fixed_height + 'px',
                'width': fixed_width + 'px'
            });
            dvp.css({
                'position': 'absolute',
                'left': (fixed_width + 20) + 'px',
                'display': 'block',
                'height': fixed_height + 'px',
                'width': fixed_width + 'px'
            });

            inner.animate({
                'left': '-=' + (fixed_width + 20)
            }, 'fast');

            var body = dvp.find('.panel-body');
            body.addClass('loading');
            $.getJSON("data/" + id + ".json", function(data) {
                body.removeClass('loading');

                var mtable = $('<table class="table">');
                mtable.append('<tr><td class="meta-label">Applicant</td><td>' + data.applicant + '</td></tr>');
                mtable.append('<tr><td class="meta-label">Date Received</td><td>' + formatDate(new Date(data.dateRcpt)) + '</td></tr>');
                dvp.find('.meta-container').html("").append(mtable);
                
                body.text(data.text);
                
                var h = dvp.height() - (dvp.find('.panel-heading').height() + mtable.height() + 20);
                body.css('height', h);
            })
        })
        
        $('#doc-dialog .doc-view-panel .panel-heading').on('click', 'a.back-link', function(evt) {
            evt.stopPropagation();
            evt.preventDefault();
            window.replaceHash(focus.id + "/docs");

            var inner = $('.panel-shifter-inner');
            inner.animate({
                'left': '0'
            }, 'fast');
        })

        /* make the embed link work */
        $('#embed-link').on('click', function(evt) {
            evt.preventDefault();
            var dialog = $('#embed-dialog');
            dialog.modal('toggle');
            dialog.find('.iframe-src').html(window.location.href);
            dialog.find('.iframe-height').html($(window).height());
            dialog.find('.iframe-width').html($(window).width());
        })

        /* check see if there's a hash and load it */
        if (window.location.hash) {
            var hparts = window.location.hash.slice(1).split("/");
            zoom(d3.selectAll('circle#circle-' + hparts[0]).datum());

            if (hparts.length > 1 && hparts[1] == "docs") {
                setTimeout(function() {
                    $(viewButton[0]).click();

                    if (hparts.length > 2) {
                        setTimeout(function() {
                            var interval = setInterval(function() {
                                var group = $('#doc-dialog .list-group');
                                if (!group.hasClass('loading')) {
                                    clearInterval(interval);
                                    var item = group.find('a[data-item-id=' + hparts[2] + ']');
                                    item.click();
                                }
                            }, 100);
                        }, 100);
                    }
                }, 100);
            }
        }
    });

    var formatDate = function(d) {
        months = ["January", "February", "March", 
            "April", "May", "June", "July", "August", "September", 
            "October", "November", "December"];

        return months[d.getMonth()] + " " + d.getDate() + ", " + d.getFullYear();
    }
})(jQuery);
