var ReactRouter = require('react-router');
var Router = ReactRouter.Router;
var Route = ReactRouter.Route;
var Link = ReactRouter.Link;
var History = ReactRouter.History;

var MatchList = require('./matchList.jsx');

module.exports = React.createClass({
    getInitialState: function () {
        return {item: null, matches: []};
    },
    componentDidMount: function () {
        window.startLoading(2);
        // load match
        var id = this.props.params.id;

        $.ajax({
            url: window.apiURLs.itemList + id,
            dataType: 'json',
            cache: false,
            success: function (data) {
                this.setState({item: data, matches: this.state.matches});
                window.finishLoading();
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(this.props.url, status, err.toString());
                window.finishLoading();
            }.bind(this)
        });

        // load related matches
        $.ajax({
            url: window.apiURLs.itemMatches + id,
            dataType: 'json',
            cache: false,
            success: function (data) {
                this.setState({item: this.state.item, matches: data.matches});
                window.finishLoading();
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(this.props.url, status, err.toString());
                window.finishLoading();
            }.bind(this)
        });
    },
    render: function () {
        if (this.state.item == null) {
            return (
                <div></div>
            )
        } else {
            return (
                <ItemDetail item={this.state.item} matches={this.state.matches}/>
            )
        }
    }
});

var ItemDetail = React.createClass({
    render: function () {
        var item = this.props.item;
        var matches = this.props.matches;

        return (
            <div>
                <div className="row">
                    <div className="col-md-2">
                        <img src={item.image}/>
                    </div>
                    <div className="col-md-10">
                        <h1>{item.localized_name}</h1>
                    </div>
                </div>
                <MatchList data={matches}/>
            </div>
        )
    }
});