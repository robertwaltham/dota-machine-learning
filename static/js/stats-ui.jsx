var Router = ReactRouter;
var DefaultRoute = Router.DefaultRoute;
var Link = Router.Link;
var Route = Router.Route;
var RouteHandler = Router.RouteHandler;

var apiURLs = {
    heroList: '',
    matchList: '',
    itemList: '',
    heroMatches: ''
};


// TODO: refactor message handling
var startLoading = function () {
};
var finishLoading = function () {
};

var spinnerOptions = {
    lines: 13 // The number of lines to draw
    , length: 28 // The length of each line
    , width: 14 // The line thickness
    , radius: 42 // The radius of the inner circle
    , scale: 1 // Scales overall size of the spinner
    , corners: 1 // Corner roundness (0..1)
    , color: '#666' // #rgb or #rrggbb or array of colors
    , opacity: 0.25 // Opacity of the lines
    , rotate: 0 // The rotation offset
    , direction: 1 // 1: clockwise, -1: counterclockwise
    , speed: 1 // Rounds per second
    , trail: 60 // Afterglow percentage
    , fps: 20 // Frames per second when using setTimeout() as a fallback for CSS
    , zIndex: 2e9 // The z-index (defaults to 2000000000)
    , className: 'spinner' // The CSS class to assign to the spinner
    , top: '50%' // Top position relative to parent
    , left: '50%' // Left position relative to parent
    , shadow: false // Whether to render a shadow
    , hwaccel: false // Whether to use hardware acceleration
    , position: 'absolute' // Element positioning
};

function render(urls) {
    // pass in URLS from django template
    apiURLs = urls;
    var routes = (
        <Route name="DotaStats" path="/" handler={DotaStats}>
            <Route name="Heroes" handler={HeroBox}/>
            <Route name="Matches" handler={MatchBox}/>
            <Route name="Items" handler={ItemBox}/>
            <Route name="Hero/:id" handler={HeroDetailBox}/>
            <DefaultRoute handler={HeroBox}/>
        </Route>
    );
    Router.run(routes, function (Handler) {
        React.render(<Handler/>, document.body);
    });
}


var DotaStats = React.createClass({
    render: function () {
        return (<div>
            <LoadingSpinner/>
            <NavBar elements={['Heroes', 'Matches', 'Items']}/>
            <ContentBody ref="body">
                <RouteHandler/>
            </ContentBody>
        </div>);
    }
});

var ContentBody = React.createClass({
    render: function () {
        return (<div className="container">{this.props.children}</div>);
    }
});

/**
 *
 */
var ItemBox = React.createClass({
    getInitialState: function () {
        return {data: []};
    },
    componentDidMount: function () {
        startLoading();
        $.ajax({
            url: apiURLs.itemList,
            dataType: 'json',
            cache: false,
            success: function (data) {
                this.setState({data: data});
                finishLoading();
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(this.props.url, status, err.toString());
                finishLoading();
            }.bind(this)
        });
    },
    render: function () {
        return (
            <div className="item-box">
                <h1>Items</h1>
                <ItemList data={this.state.data}/>
            </div>
        )
    }
});

var ItemList = React.createClass({
    render: function () {
        var itemNodes = this.props.data.map(function (item) {
            return (
                <div className="col-md-2 col-sm-3">
                    <a href={item.url}>
                        <img src={item.image}/>
                        {item.localized_name}
                    </a>

                </div>
            );
        });
        return (
            <div className="item-list">
                {itemNodes}
            </div>
        );
    }
});

/**
 *
 */
var MatchBox = React.createClass({
    getInitialState: function () {
        return {data: []};
    },
    componentDidMount: function () {
        startLoading();
        $.ajax({
            url: apiURLs.matchList,
            dataType: 'json',
            cache: false,
            success: function (data) {
                this.setState({data: data.results});
                finishLoading();
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(this.props.url, status, err.toString());
                finishLoading();
            }.bind(this)
        });
    },
    render: function () {
        return (
            <div className="match-box">
                <h1>Matches</h1>
                <MatchList data={this.state.data}/>
            </div>
        );
    }
});


var MatchList = React.createClass({
    render: function () {
        var matchNodes = this.props.data.map(function (match) {
            return (
                <Match key={match.match_id} match={match}/>
            );
        });
        return (
            <div className="hero-list">
                {matchNodes}
            </div>
        );
    }
});

var Match = React.createClass({
    render: function () {
        var match = this.props.match;
        var playerNodes = match.playerinmatch.map(function (player) {
            var hero = player.hero;
            return (
                <MatchHeroImage hero={hero}/>
            )
        });
        return (
            <div className="col-md-12">
                <div className="row">
                    <div className="col-md-2">
                        <a href={match.url}>
                            {match.match_id}
                        </a>
                    </div>
                    <div className="col-md-10">
                        {playerNodes}
                    </div>
                </div>
            </div>
        )
    }
});

/**
 *
 */
var HeroList = React.createClass({
    render: function () {
        var heroNodes = this.props.data.map(function (hero) {
            return (
                <Hero key={hero.hero_id} hero={hero}/>
            );
        });
        return (
            <div className="hero-list">
                {heroNodes}
            </div>
        );
    }
});

var HeroBox = React.createClass({
    getInitialState: function () {
        return {data: []};
    },
    componentDidMount: function () {
        startLoading();
        $.ajax({
            url: apiURLs.heroList,
            dataType: 'json',
            cache: false,
            success: function (data) {
                this.setState({data: data});
                finishLoading();
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(this.props.url, status, err.toString());
                finishLoading();
            }.bind(this)
        });
    },
    render: function () {
        return (
            <div className="hero-box">
                <h1>Heroes</h1>
                <HeroList data={this.state.data}/>
            </div>
        );
    }
});

var Hero = React.createClass({
    render: function () {
        var hero = this.props.hero;
        return (
            <div className="col-md-3 col-sm-4">
                <Link to="Hero/:id" params={{id: hero.hero_id, url:hero.url}}>
                    <img src={hero.hero_image}/>

                    <div>{hero.localized_name}</div>
                </Link>
            </div>
        )
    }
});


/**
 *
 */
var NavBar = React.createClass({
    elementClick: function (i) {
        this.setState({active: this.props.elements[i]});
        //this.props.transitions[i](this.state.active);
    },
    getInitialState: function () {
        return {active: this.props.elements[0]}
    },
    renderChildren: function () {
        return this.props.elements.map(function (element, i) {
            return (
                <li><Link to={element}>{element}</Link></li>
            );
        }, this);
    },
    render: function () {
        return (
            <nav className="navbar navbar-default">
                <div className="container-fluid">
                    <div className="navbar-header">
                        <button type="button" className="navbar-toggle collapsed" data-toggle="collapse"
                                data-target="#bs-example-navbar-collapse-1" aria-expanded="false">
                            <span className="sr-only">Toggle navigation</span>
                            <span className="icon-bar"></span>
                            <span className="icon-bar"></span>
                            <span className="icon-bar"></span>
                        </button>
                        <a className="navbar-brand" href="#">Dota Stats</a>
                    </div>
                    <div className="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
                        <ul className="nav navbar-nav">
                            {this.renderChildren()}
                        </ul>
                    </div>
                </div>
            </nav>
        )
    }
});

/**
 *
 */
var HeroDetailBox = React.createClass({
    getInitialState: function () {
        return {hero: null, matches: []};
    },
    componentDidMount: function () {
        this.loadHeroDetails(this.props.params.id);
    },
    componentWillReceiveProps: function (props) {
        this.loadHeroDetails(props.params.id);
    },
    loadHeroDetails: function (id) {
        startLoading();
        // load hero
        $.ajax({
            url: apiURLs.heroList + id,
            dataType: 'json',
            cache: false,
            success: function (data) {
                this.setState({hero: data, matches: this.state.matches});
                finishLoading();
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(this.props.url, status, err.toString());
                finishLoading();
            }.bind(this)
        });

        // load related matches
        $.ajax({
            url: apiURLs.heroMatches + id,
            dataType: 'json',
            cache: false,
            success: function (data) {
                this.setState({hero: this.state.hero, matches: data.matches});
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }.bind(this)
        });
    },
    render: function () {
        if (this.state.hero == null) {
            return (
                <div></div>
            )
        } else {
            return (
                <HeroDetail hero={this.state.hero} matches={this.state.matches}/>
            )
        }

    }
});

var HeroDetail = React.createClass({
    render: function () {
        var hero = this.props.hero;
        var matches = this.props.matches;
        var matchNodes = matches.map(function (match) {
            var matches = match.playerinmatch.map(function (playerinmatch) {
                var hero = playerinmatch.hero;
                return (
                    <MatchHeroImage hero={hero}/>
                )
            });

            return (

                <div className="row">
                    <div className="col-md-2">
                        {match.match_id}
                    </div>
                    <div className="col-md-10">
                        {matches}
                    </div>
                </div>
            )
        });


        return (
            <div className="col-md-12">
                <div className="row">
                    <div className="col-md-2">
                        <img src={hero.hero_image}/>
                    </div>
                    <div className="col-md-10">
                        <h2>{hero.localized_name}</h2>
                    </div>
                </div>
                <div className="row">
                    <h3>Recent Matches</h3>
                </div>
                {matchNodes}
            </div>
        )
    }
});


var MatchHeroImage = React.createClass({
    render: function () {
        var hero = this.props.hero;
        return (
            <Link to="Hero/:id" params={{id: hero.hero_id, url:hero.url}}>
                <img src={hero.small_hero_image}/>
            </Link>
        )
    }
});


var LoadingSpinner = React.createClass({
    _startLoading: function () {
        this.setState({count: this.state.count + 1});
    },
    _finishLoading: function () {
        this.setState({count: this.state.count - 1});
    },
    getInitialState: function () {
        return {count: 0};
    },
    componentDidMount: function () {
        var spinner = new Spinner(spinnerOptions).spin(React.findDOMNode(this.refs.spinAnchor));
        // bind message handlers for showing/hiding spinner
        startLoading = this._startLoading.bind(this);
        finishLoading = this._finishLoading.bind(this)
    },
    render: function () {
        var hidden = this.state.count > 0 ? {} : {display: 'none'};
        return (
            <div style={hidden} className="loading-spinner-wrap" ref="spinAnchor"></div>
        )
    }
});