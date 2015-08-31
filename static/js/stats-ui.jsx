var DotaStats = React.createClass({
    showHeroes: function (state) {
        if (state !== 'Heroes') {
            React.render(
                <DotaStats urls={this.props.urls}><HeroBox url={this.props.urls[0]}/></DotaStats>,
                document.body
            );
        }
    },
    showMatches: function (state) {
        if (state !== 'Matches') {
            React.render(
                <DotaStats urls={this.props.urls}><MatchBox url={this.props.urls[1]}/></DotaStats>,
                document.body
            );
        }
    },
    showItems: function (state) {
        if (state !== 'Items') {
            React.render(
                <DotaStats urls={this.props.urls}><ItemBox url={this.props.urls[2]}/></DotaStats>,
                document.body
            );
        }
    },
    render: function () {
        return (<div>
            <NavBar elements={['Heroes', 'Matches', 'Items']}
                    transitions={[this.showHeroes, this.showMatches, this.showItems]}/>
            <ContentBody ref="body">{this.props.children}</ContentBody>
        </div>);
    }
});

var ItemBox = React.createClass({
    getInitialState: function () {
        return {data: []};
    },
    componentDidMount: function () {
        $.ajax({
            url: this.props.url,
            dataType: 'json',
            cache: false,
            success: function (data) {
                this.setState({data: data});
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }.bind(this)
        });
    },
    render:function(){
        return (
            <div className="item-box">
                <h1>Items</h1>
                <ItemList data={this.state.data} />
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

var MatchBox = React.createClass({
    getInitialState: function () {
        return {data: []};
    },
    componentDidMount: function () {
        $.ajax({
            url: this.props.url,
            dataType: 'json',
            cache: false,
            success: function (data) {
                this.setState({data: data.results});
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(this.props.url, status, err.toString());
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
        var playerNodes= match.playerinmatch.map(function(player){
            var hero = player.hero;
            return (
                <a href={hero.url}>
                    <img src={hero.small_hero_image}/>
                </a>
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
        $.ajax({
            url: this.props.url,
            dataType: 'json',
            cache: false,
            success: function (data) {
                this.setState({data: data});
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(this.props.url, status, err.toString());
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
                <a href={hero.url}>
                    <img src={hero.hero_image}/>

                    <div>{hero.localized_name}</div>
                </a>
            </div>
        )
    }
});
var ContentBody = React.createClass({
    render: function () {
        return (<div className="container">{this.props.children}</div>);
    }
});

var NavBar = React.createClass({
    elementClick: function (i) {
        this.setState({active: this.props.elements[i]});
        this.props.transitions[i](this.state.active);
    },
    getInitialState: function () {
        return {active: this.props.elements[0]}
    },
    renderChildren: function () {
        return this.props.elements.map(function (element, i) {
            return (
                <NavElement key={i} active={this.state.active} name={element}
                            click={this.elementClick.bind(this, i)}/>
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

var NavElement = React.createClass({
    render: function () {
        var active = this.props.active === this.props.name ? 'active' : '';
        return (
            <li onClick={this.props.click} className={active}>
                <a className="navbar-brand" href="#">{this.props.name}</a>
            </li>
        );
    }
});
