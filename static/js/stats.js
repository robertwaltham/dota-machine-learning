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
        date_count:[],
        init: function (urls, heroes, date_count) {
            stats.heroes = heroes;
            stats.date_count = date_count;
            $.extend(stats.urls, {}, urls);

            rivets.binders.count = function (el, value) {
                $(el).html(_.keys(value).length);
            };

            rivets.bind($('body'), {
                stats:stats
            });

            var $hero = [$('#str-hero'), $('#agi-hero'), $('#int-hero')],
                hero_element = ['', '', ''],
                hero_count = [0,0,0],
                row_count = 3;

            for(var i = 0; i < stats.heroes.length; i++){
                var hero = stats.heroes[i],
                    attribute = hero['primary_attribute'];


                if(hero_count[attribute] % row_count === 0){
                    hero_element[attribute] += '<div class="row">';
                }

                hero_element[attribute] += '<div class="col-md-4"><a href="' + hero.link + '"><img src="' + hero.image
                    + '"><div>'+ hero.name +'</div></a></div>';

                hero_count[attribute] += 1;

                if(hero_count[attribute] % row_count === 0){
                    hero_element[attribute] += '</div>';
                }
            }

            $hero[0].append(hero_element[0]);
            $hero[1].append(hero_element[1]);
            $hero[2].append(hero_element[2]);

            var $date_sel = $('#date-count'),
                date_list = '';
            _.each(stats.date_count, function(date){
                date_list += '<div class="row"><div class="col-md-6">'+date.start_time+
                    '</div><div class="col-md-6">'+date.created_count+'</div></div>'
            });
            $date_sel.append(date_list);

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
