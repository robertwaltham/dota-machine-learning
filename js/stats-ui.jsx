/** @jsx React.DOM */

var React = require('react');
window.React = React;

var ReactRouter = require('react-router');
var Router = ReactRouter.Router;
var Route = ReactRouter.Route;
var Link = ReactRouter.Link;
var History = ReactRouter.History;

var Spinner = require('spin');
var _ = require('underscore');

var ItemBox = require('./itemBox.jsx');
var HeroBox = require('./heroBox.jsx');
var MatchBox = require('./matchBox.jsx');
var StatusBox = require('./statusDetail.jsx');

var ItemDetailBox = require('./itemDetail.jsx');
var HeroDetailBox = require('./heroDetail.jsx');
var MatchDetailBox = require('./matchDetail.jsx');

var NavBar = require('./navBar.jsx');



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


function render(urls, user) {
    // pass in URLS from django template
    window.apiURLs = urls;
    window.logged_in_user = user;
    React.render(<Router>
                    <Route name="DotaStats" path="/" component={DotaStats}>
                        <Route path="Heroes" component={HeroBox}/>
                        <Route path="Matches" component={MatchBox}/>
                        <Route path="Items" component={ItemBox}/>
                        <Route path="Hero/:id" component={HeroDetailBox}/>
                        <Route path="Match/:id" component={MatchDetailBox}/>
                        <Route path="Item/:id" component={ItemDetailBox}/>
                        <Route path="Status" component={StatusBox}/>
                    </Route>
                </Router>, document.getElementById('container'));
}

window.renderDotaStats = render;


var DotaStats = React.createClass({
    render: function () {
        return (<div>
            <LoadingSpinner/>
            <ContentBody ref="body">
                <NavBar/>
                {this.props.children || <HeroBox/>}
            </ContentBody>
        </div>);
    }
});

var ContentBody = React.createClass({
    render: function () {
        return (<div className="container">{this.props.children}</div>);
    }
});

var LoadingSpinner = React.createClass({
    _startLoading: function (n) {
        if (!n) n = 1;
        this.setState({count: this.state.count + n});
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
        window.startLoading = this._startLoading;
        window.finishLoading = this._finishLoading;
    },
    render: function () {
        var hidden = this.state.count > 0 ? {} : {display: 'none'};
        return (
            <div style={hidden} className="loading-spinner-wrap" ref="spinAnchor"></div>
        )
    }
});



