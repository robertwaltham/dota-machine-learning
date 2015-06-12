var stats = null;

(function () {
    stats = {
        urls: {
            getMatch: '',
            processMatch: '',
            staticData: '',
            buildModel:''
        },
        heroes:[],
        init: function (urls, heroes) {
            stats.heroes = heroes;
            $.extend(stats.urls, {}, urls);

            rivets.binders.count = function (el, value) {
                $(el).html(_.keys(value).length);
            };

            rivets.bind($('body'), {
                stats:stats
            });

            var $hero = [$('#str-hero'), $('#agi-hero'), $('#int-hero')];
            _.map(stats.heroes, function(hero){
                $hero[hero['primary_attribute']].append('<tr><td><img src="' + hero.image + '"></td></tr>');
            });


        },
        events: {
            getMatches: function () {
                $.getJSON(stats.urls.getMatch)
                    .done(function (data) {
                        alert(data);
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
                        alert("Done");
                    })
                    .fail(function () {
                        console.log("error");
                    })
                    .always(function () {
                    });
            },
            buildModel: function () {
                $.getJSON(stats.urls.buildModel)
                    .done(function (data) {
                        alert(data.task_id);
                    })
                    .fail(function () {
                        console.log("error");
                    })
                    .always(function () {
                    });
            },
            getStaticData: function(){
                $.getJSON(stats.urls.staticData)
                    .done(function (data) {
                        alert('Loaded: ' + data.heroes + ' Heroes, ' + data.items + ' Items');
                        console.log(data);
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
