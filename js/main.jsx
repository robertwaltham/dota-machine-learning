/** @jsx React.DOM */

var React = require('react');
// Here we put our React instance to the global scope. Make sure you do not put it
// into production and make sure that you close and open your console if the
// DEV-TOOLS does not display
window.React = React;

// not using an ES6 transpiler
var ReactRouter = require('react-router');
var Router = ReactRouter.Router;
var Route = ReactRouter.Route;
var Link = ReactRouter.Link;


var DotaStats = React.createClass({
    render: function () {
        return (<div>
            {this.props.children}
        </div>);
    }
});

var HeroBox = React.createClass({
    render: function () {
        return (
            <h1>Hero!</h1>
        )
    }
});

function render() {
    // pass in URLS from django template
    React.render((
        <Router>
            <Route path="/" component={DotaStats}>
                <Route component={HeroBox}/>
            </Route>
        </Router>
    ), document.getElementById('container'))
}

render();