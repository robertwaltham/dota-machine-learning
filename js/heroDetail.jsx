var ReactRouter = require('react-router');
var Router = ReactRouter.Router;
var Route = ReactRouter.Route;
var Link = ReactRouter.Link;
var History = ReactRouter.History;

var MatchList = require('./matchList.jsx');

module.exports = React.createClass({
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
        window.startLoading(2);
        // load hero
        $.ajax({
            url: window.apiURLs.heroList + id,
            dataType: 'json',
            cache: false,
            success: function (data) {
                this.setState({hero: data, matches: this.state.matches});
                window.finishLoading();
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(this.props.url, status, err.toString());
                window.finishLoading();
            }.bind(this)
        });

        // load related matches
        $.ajax({
            url: window.apiURLs.heroMatches + id,
            dataType: 'json',
            cache: false,
            success: function (data) {
                this.setState({hero: this.state.hero, matches: data.matches});
                window.finishLoading();
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(this.props.url, status, err.toString());
                window.finishLoading();
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

        return (
            <div className="col-md-12">
                <div className="row">
                    <div className="col-md-2">
                        <img className="hero-image" src={hero.hero_image}/>
                    </div>
                    <div className="col-md-10">
                        <h2>{hero.localized_name}</h2>
                    </div>
                </div>
                <div className="row">
                    <h3>Recent Matches</h3>
                </div>
                <MatchList data={matches}/>
            </div>
        )
    }
});