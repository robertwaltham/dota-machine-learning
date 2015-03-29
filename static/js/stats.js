var stats = null;

(function () {
    stats = {
        matches: {},
        processed_matches:0,
        urls: {
            getMatch: '',
            processMatch: ''
        },
        init: function (urls, matches, processed_matches) {
            stats.processed_matches = processed_matches;
            $.extend(stats.urls, {}, urls);
            _.each(matches, function(match, index, list){
                stats.matches[match.pk] = match.fields;
            });

            rivets.binders.count = function (el, value) {
                $(el).html(_.keys(value).length);
            };

            rivets.bind($('body'), {
                events: stats.events,
                matches: stats.matches,
                processed_matches: stats.processed_matches
            })
        },
        events: {
            getMatches: function () {
                $.getJSON(stats.urls.getMatch)
                    .done(function (data) {
                        _.each(data, function(match, index, list){
                            console.log(match.pk);
                            stats.matches[match.pk] = match.fields;
                        });
                        console.log(data);
                    })
                    .fail(function () {
                        console.log("error");
                    })
                    .always(function () {
                    });
            },
            processMatch: function () {
                $.getJSON(stats.urls.processMatch)
                    .done(function (data) {
                        _.each(data, function(match, index, list){
                            console.log(match.pk);
                            stats.matches[match.pk] = match.fields;
                        });
                        stats.processed_matches++;
                    })
                    .fail(function () {
                        console.log("error");
                    })
                    .always(function () {
                    });
            }
        }
    }
})();
