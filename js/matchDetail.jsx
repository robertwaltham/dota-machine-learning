var ReactRouter = require('react-router');
var Router = ReactRouter.Router;
var Route = ReactRouter.Route;
var Link = ReactRouter.Link;
var History = ReactRouter.History;

module.exports = React.createClass({
    getInitialState: function () {
        return {match: null};
    },
    componentDidMount: function () {
        window.startLoading();
        // load match
        $.ajax({
            url: window.apiURLs.matchList + this.props.params.id,
            dataType: 'json',
            cache: false,
            success: function (data) {
                this.setState({match: data});
                window.finishLoading();
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(this.props.url, status, err.toString());
                window.finishLoading();
            }.bind(this)
        });
    },
    render: function () {
        if (this.state.match == null) {
            return (
                <div></div>
            )
        } else {
            return (
                <MatchDetail match={this.state.match}/>
            )
        }
    }
});

var MatchDetail = React.createClass({
    render: function () {
        var match = this.props.match;
        var teams = _.partition(match.playerinmatch, function (playerinmatch) {
            return playerinmatch.player_slot < 128; // 128 and above is on team dire
        });
        var radiantWin = match.radiant_win ? 'Radiant Win' : 'Dire Win';
        return (
            <div>
                <div className="row">
                    <div className="col-md-12">
                        <h1>Match {match.match_id} Detail</h1>
                    </div>
                </div>
                <div className="row">
                    <div className="col-md-12">
                        <ul>
                            <li>Start Time: {match.start_time}</li>
                            <li>Sequence Number: {match.match_seq_num}</li>
                            <li>Duration: {match.duration}s</li>
                            <li>First Blood: {match.first_blood_time}s</li>
                            <li>Lobby Type: {match.lobby_type}</li>
                            <li>Human Players: {match.human_players}</li>
                            <li>Game Mode: {match.game_mode}</li>
                            <li>Skill: {match.skill}</li>
                            <li>{radiantWin}</li>
                        </ul>
                    </div>
                </div>
                <div className="row">
                    <div className="col-md-6">
                        <h3>Radiant</h3>
                        <MatchTeamDetail team={teams[0]}/>
                    </div>
                    <div className="col-md-6">
                        <h3>Dire</h3>
                        <MatchTeamDetail team={teams[1]}/>
                    </div>
                </div>
            </div>

        )

    }
});

var MatchTeamDetail = React.createClass({
    render: function () {
        var team = this.props.team;
        var teamNodes = team.map(function (player) {
            return (
                <MatchPlayerDetail key={player.player_slot} player={player}/>
            )
        });
        return (
            <div>{teamNodes}</div>
        )
    }
});

var MatchPlayerDetail = React.createClass({
    render: function () {
        var player = this.props.player;
        return (
            <div className="row">
                <div className="col-md-5">
                    <MatchPlayerHeroDetail hero={player.hero} use_small_image={true}/>
                </div>
                <div className="col-md-7">
                    <MatchPlayerItemDetail item={player.item_0}/>
                    <MatchPlayerItemDetail item={player.item_1}/>
                    <MatchPlayerItemDetail item={player.item_2}/>
                    <MatchPlayerItemDetail item={player.item_3}/>
                    <MatchPlayerItemDetail item={player.item_4}/>
                    <MatchPlayerItemDetail item={player.item_5}/>
                </div>
            </div>
        )
    }
});

var MatchPlayerItemDetail = React.createClass({
    render: function () {
        var item = this.props.item;
        if (item && item.item_id > 0) {
            return (
                <div className="match-detail-item">
                    <Link to={`/Item/${item.item_id}`} params={{id:item.item_id, url:item.url}}>
                        <img src={item.small_image}/>
                    </Link>
                </div>

            )
        } else {
            return (
                <div className="match-detail-item empty">
                    &nbsp;
                </div>
            )
        }

    }
});

var MatchPlayerHeroDetail = React.createClass({
    render: function () {
        var hero = this.props.hero;
        var image = this.props.use_small_image ? hero.small_hero_image : hero.hero_image;
        var imageClass = this.props.use_small_image ? 'hero-image-small' : 'hero-image';

        return (
            <Link to={`/Hero/${hero.hero_id}`} params={{id: hero.hero_id, url:hero.url}}>
                <div className="row">
                    <div className="col-md-4">
                        <img className={imageClass} src={image}/>
                    </div>
                    <div className="col-md-8">
                        <div>{hero.localized_name}</div>
                    </div>
                </div>
            </Link>
        )
    }
});
