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
    // grab the query dict and see if this is a special one
    var queryDict = {};
    location.search.substr(1).split("&").forEach(function(item) {queryDict[item.split("=")[0]] = item.split("=")[1]});
    var dataset = queryDict.t ? queryDict.t : 'tree';
    
    var stylesXHR = $.getJSON('assets/styles.json');
    var dataXHR = $.getJSON('assets/' + dataset + '.json');

    $.when(stylesXHR, dataXHR).done(function(stylesResult, dataResult) {
        styles = stylesResult[0];
        data = dataResult[0];

        // add indices for color
        $.each(data, function(idx, item) {
            item.idx = idx;
        })
        var getIndex = function(node) {
            return typeof(node.idx) !== "undefined" ? node.idx : getIndex(node.parent);
        }

        var $svg = $('svg');

        var margin = 20,
            width = $svg.width(),
            height = $svg.height();

        var diameter = Math.min(height, width);

        var format = d3.format("0,000");
        var percentFormat = d3.format(".4p");


        var pack = d3.layout.pack()
            .padding(2)
            .size([width, height])
            .value(function(d) { return d.size; })

        var svg = d3.select($svg[0])
            .append("g")
                .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")")
                .attr('class', 'main');

        var annotations = d3.select($svg[0])
            .append("g")
            .classed("annotations", true);

        var root = {'children': data, 'size': $.map(data, function(el) { return el.size; }).reduce(function(a, b) { return a + b; }, 0)};

        var focus = root,
            nodes = pack.nodes(root),
            view;

        var max_depth = d3.max(nodes, function(d) { return d.depth; })
        var color_keys = ["yellows", "oranges", "reds", "pinks", "magentas", "blues", "cyans", "teals", "mints", "greens"];
        var colors = $.map(color_keys, function(c) {
            var color = styles.colors.network_graph[c];
            return d3.scale.linear()
                .domain([1, max_depth])
                .range([color[0].hex, color[2].hex])
                .interpolate(d3.interpolateHcl);
        });

        //var shadow = '0 1px 0 rgba(255,255,255,1), 1px 0 0 rgba(255,255,255,1), -1px 0 0 rgba(255,255,255,1), 0 -1px 0 rgba(255,255,255,1)';
        var shadow = '0 1px 0 rgba(255,255,255,0.25), 1px 0 0 rgba(255,255,255,0.25), -1px 0 0 rgba(255,255,255,0.25), 0 -1px 0 rgba(255,255,255,0.25)';
        //var shadow = '';

        var findVisibleLabel = function(d) {
            var l = d3.selectAll('#label-' + d.id);
            var parent = d3.select(l[0][0].parentNode);
            if (parent.style('display') == 'block') {
                return l;
            } else if (d.parent && d.parent.id) {
                return findVisibleLabel(d.parent);
            } else {
                return null;
            }
        }

        var circle = svg.selectAll("circle")
            .data(nodes)
          .enter().append("circle")
            .attr('id', function(d) { return d.id ? 'circle-' + d.id : null; })
            .attr("class", function(d) { return d.parent ? d.children ? "node" : "node node--leaf" : "node node--root"; })
            .style("fill", function(d) { return d.parent ? (d.color ? d.color : colors[getIndex(d)](d.depth)) : "none"; })
            .style("stroke", function(d) { return d.parent ? (d.color ? d3.rgb(d.color).darker(1) : colors[getIndex(d)](d.depth + 2)) : "none"; })
            .style("stroke-width", function(d) { return d.parent ? "1" : "none"; })
            .style("pointer-events", function(d) { return d.parent ? "auto" : "none"})
            .on("click", function(d) { if (focus !== d) zoom(d), d3.event.stopPropagation(); })
            .on('mouseover', function(d, i) {
                var l = findVisibleLabel(d);
                if (!l) return;

                var parent = d3.select(l[0][0].parentNode);

                if (parent.style('display') == 'block') {
                    var group = d3.selectAll('#label-group-' + l.data()[0].id);
                    group[0][0].parentNode.appendChild(group[0][0]);

                    l.style('background', 'rgba(255,255,255,0.85)');
                }
            })
            .on('mouseout', function(d, i) {
                var l = findVisibleLabel(d);
                if (!l) return;

                l.style('background', '');
            });

        var text = svg.selectAll("g.label-group")
            .data(nodes)
            .enter()
                .append("g")
                    .classed("label-group", true)
                    .attr('id', function(d) { return d.id ? 'label-group-' + d.id : null; })
                    .style('pointer-events', 'none')
                    .append("foreignObject")
                        .style("display", function(d) { return d.parent === root ? "block" : "none"; })
                        .classed('tlabel', true)
                        .attr("width", 200)
                        .attr('x', -100)
                        .attr('y', -20)
                        .attr("height", 100)
                        .append("xhtml:div")
                        .attr('id', function(d) { return d.id ? 'label-' + d.id : null; })
                        .text(function(d, i) { return d.keywords ? d.keywords.join(", ") : ""; });


        /* titles and annotations */
        var title = annotations
            .append("foreignObject")
            .classed('title', true)
            .style('pointer-events', 'none')
            .attr('height', 100)
            .attr('width', '100%')
            .append("xhtml:div")
                .text("")
                .style("display", "none")
                .style("font-size", "200%")

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
            .html('<button class="btn-sunlight"><i class="glyphicon glyphicon-list-alt"></i> <span class="button-label"></span></button>');
        var viewButton = viewButtonArea.selectAll('button');
        viewButton.style('display', 'none')


        var node = svg.selectAll("circle,.tlabel");

        d3.select($svg[0])
            .on("click", function() { zoom(root); });

        zoomTo([root.x, root.y, root.r * 2 + margin]);
        updateCount(root);
        svg.classed('zoom0', true);

        /* response to interactivity in the graph */
        var view_d = null;
        function updateCount (d) {
            stats.text(format(d.size) + " documents (" + percentFormat(d.size / root.size) + ")");
            view_d = d;
            var box = stats.node().getBBox();
            viewButtonArea
                .attr('x', 30 + box.width)
                .attr('y', height - 25 - box.height)
                .style('display', null)
                .selectAll('.button-label')
                    .text(d.sample ? "view sample" : "view all");
        }

        function zoom(d) {
            var focus0 = focus; focus = d;

            if (focus0) svg.classed('zoom' + focus0.depth, false);
            svg.classed('zoom' + d.depth, true);

            d3.selectAll('circle').classed('selected', false);
            if (focus.parent) {
                d3.selectAll('circle#circle-' + d.id).classed('selected', true);
                viewButton.style('display', '');
                window.replaceHash(d.id);
            } else {
                title.style('display', 'none');
                viewButton.style('display', 'none');
                window.replaceHash("");
            }

            updateCount(d);

            var transition = d3.transition()
                .duration(750)
                .tween("zoom", function(d) {
                  var i = d3.interpolateZoom(view, [focus.x, focus.y, focus.r * 2 + margin]);
                  return function(t) { zoomTo(i(t)); };
                });

            var pulsated = false;
            transition.selectAll(".main .tlabel")
              .filter(function(d) { return d.parent === focus || (d == focus && (!d.children)) || this.style.display === "block"; })
                .style("opacity", function(d) { return (d.parent === focus || (d == focus && (!d.children))) ? 1 : 0; })
                .each("start", function(d) { if (d.parent === focus || (d == focus && (!d.children))) this.style.display = "block"; })
                .each("end", function(d, i) {
                    // text display
                    if (d.parent !== focus && !(d.parent === focus || (d == focus && (!d.children)))) this.style.display = "none";
                    
                    // pulsate the title
                    if (!pulsated && focus.parent) {
                        title
                            .style('display', 'block')
                            .text(focus.keywords.join(", "));
                        title.transition()
                            .styleTween("background", function() { return function(a,b) { return "rgba(255,255,255," + d3.interpolate(0.25, 0.75)(a,b); }; })
                            .each('end', function() {
                                title.transition()
                                    .styleTween("background", function() { return function(a,b) { return "rgba(255,255,255," + d3.interpolate(0.75, 0.25)(a,b); }; })
                            });
                    }
                });

            d3.selectAll('.tlabel div').style('background', '');
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
                group.html("");

                var addItems = function(data) {
                    group.append(
                        data.items.map(function(item) { return '<a data-item-id="' + item.id + '"" href="#' + item.id + '" class="list-group-item">' + item.title + '<i class="glyphicon glyphicon-chevron-right pull-right"></i></a>' }).join("")
                    );
                    group.find('a.next').remove();
                    if (data.next) {
                        var next = $('<a>');
                        next.css({'display': 'none'}).addClass('next').attr('href', data.next);
                        group.append(next);
                    }
                }

                $.getJSON(dataset + "_data/" + view_d.id + "-p0.json", function(tree_data) {
                    group.removeClass('loading');
                    addItems(tree_data);

                    var origin = false;
                    if (tree_data.links && tree_data.links.length) {
                        origin = '; ';
                        if (tree_data.links.length == 1) {
                            origin = origin + '<a target="_blank" href="' + tree_data.links[0] + '">view origin document</a>';
                        } else {
                            origin = origin + 'view origin documents: ';
                            origin = origin + tree_data.links.map(function(link, idx) { return '<a target="_blank" href="' + tree_data.links[0] + '">[' + (idx + 1) + ']</a>'}).join(' ');
                        }
                    }

                    dialog.find('.cluster-size').html(format(tree_data.full_size) + " documents" + (origin ? origin : ''));
                });

                group.bind('scroll', function() {
                    if($(this).scrollTop() + $(this).innerHeight() >= this.scrollHeight) {
                        if (!group.hasClass('loading')) {
                            group.addClass('loading');
                            var next = group.find('a.next');
                            if (next.length) {
                                $.getJSON(dataset + '_data/' + next.attr('href'), function(data) {
                                    group.removeClass('loading');
                                    addItems(data);
                                })
                            }
                        }
                    }
                })
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
                'width': fixed_width + 'px',
                'visibility': 'visible'
            });

            inner.animate({
                'left': '-=' + (fixed_width + 20)
            }, 'fast');

            var body = dvp.find('.panel-body');
            body.addClass('loading');
            $.getJSON("http://54.166.152.78/data/" + id + ".json", function(data) {
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
            }, 'fast', 'swing', function() {
                inner.find('.doc-view-panel').css('visibility', 'hidden');
            });
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
        /* make the new window link work */
        $('#new-link').on('click', function(evt) {
            evt.preventDefault();
            window.open(window.location.href);
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
