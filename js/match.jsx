var ReactRouter = require('react-router');
var Router = ReactRouter.Router;
var Route = ReactRouter.Route;
var Link = ReactRouter.Link;
var History = ReactRouter.History;


module.exports = React.createClass({
    render: function () {
        var match = this.props.match;
        var playerNodes = match.playerinmatch.map(function (player) {
            var hero = player.hero;
            return (
                <MatchHeroImage key={hero.hero_id} hero={hero}/>
            )
        });
        return (
            <div key={match.match_id} className="col-md-12">
                <div className="row">
                    <div className="col-md-2">
                        <Link to={`/Match/${match.match_id}`} params={{id:match.match_id, url:match.url}}>
                            {match.match_id}
                        </Link>
                    </div>
                    <div className="col-md-10">
                        {playerNodes}
                    </div>
                </div>
            </div>
        )
    }
});

var MatchHeroImage = React.createClass({
    render: function () {
        var hero = this.props.hero;
        return (
            <Link to={`/Hero/${hero.hero_id}`} params={{id: hero.hero_id, url:hero.url}}>
                <img className="hero-image-small" src={hero.small_hero_image}/>
            </Link>
        )
    }
});