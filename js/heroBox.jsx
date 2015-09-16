var ReactRouter = require('react-router');
var Router = ReactRouter.Router;
var Route = ReactRouter.Route;
var Link = ReactRouter.Link;
var History = ReactRouter.History;

module.exports  = React.createClass({
    getInitialState: function () {
        return {data: []};
    },
    componentDidMount: function () {
        window.startLoading();
        $.ajax({
            url: window.apiURLs.heroList,
            dataType: 'json',
            cache: false,
            success: function (data) {
                this.setState({data: data});
                window.finishLoading();
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(this.props.url, status, err.toString());
                window.finishLoading();
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

var HeroList = React.createClass({
    render: function () {
        var heroNodes = this.props.data.map(function (hero) {
            return (
                <div key={hero.hero_id} className="col-md-3 col-sm-4">
                    <Hero key={hero.hero_id} hero={hero}/>
                </div>
            );
        });
        return (
            <div className="hero-list">
                {heroNodes}
            </div>
        );
    }
});


var Hero = React.createClass({
    render: function () {
        var hero = this.props.hero;
        var image = this.props.use_small_image ? hero.small_hero_image : hero.hero_image;
        var imageClass = this.props.use_small_image ? 'hero-image-small' : 'hero-image';

        return (
            <Link to={`/Hero/${hero.hero_id}`} params={{id: hero.hero_id, url:hero.url}}>
                <img className={imageClass} src={image}/>

                <div>{hero.localized_name}</div>
            </Link>
        )
    }
});
