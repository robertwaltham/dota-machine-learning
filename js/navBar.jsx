var ReactRouter = require('react-router');
var Router = ReactRouter.Router;
var Route = ReactRouter.Route;
var Link = ReactRouter.Link;
var History = ReactRouter.History;

module.exports = React.createClass({
    elementClick: function (i) {
        this.setState({elements: elements, active: this.state.elements[i], user: this.state.user});
    },
    getInitialState: function () {
        var elements = window.logged_in_user ? ['Heroes', 'Matches', 'Items', 'Status'] : ['Heroes', 'Matches', 'Items'];
        return {elements: elements, active: elements[0], user: window.logged_in_user}
    },
    renderChildren: function () {
        return this.state.elements.map(function (element, i) {
            return (
                <NavTab key={i} to={`/${element}`}>{element}</NavTab>
            );
        }, this);
    },
    login: function (e) {
        e.preventDefault();
        var data = $('#login-form').serialize();

        window.startLoading();
        $.ajax({
            url: window.apiURLs.login,
            data: data,
            processData: false,
            type: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            success: function (data) {
                window.finishLoading();
                this.setState({
                    elements: ['Heroes', 'Matches', 'Items', 'Status'],
                    active: this.state.active,
                    user: data
                });
            },
            error: function (response, data) {
                window.finishLoading();
                var text = '';
                _.each(response.responseJSON.errors, function (element, index, list) {
                    if (index == '__all__') {
                        text += element;
                    } else {
                        text += index + ' : ' + element + '\n';
                    }
                });
                alert(text);
            }

        });
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
                        <ul className="nav navbar-nav navbar-right">
                            <NavBarUserStatus login={this.login} user={this.state.user}/>
                        </ul>
                    </div>
                </div>
            </nav>
        )
    }
});


var NavTab = React.createClass({
    mixins: [History],
    render: function () {
        var isActive = this.history.isActive(this.props.to, this.props.params, this.props.query);
        var className = isActive ? 'active' : '';
        var link = (
            <Link {...this.props} />
        );
        return (<li className={className}>{link}</li>);
    }

});

var NavBarUserStatus = React.createClass({
    render: function () {
        var csrftoken = getCookie('csrftoken');

        if (this.props.user) {
            return (
                <li className="dropdown active">
                    <a href="#" className="dropdown-toggle" data-toggle="dropdown">{this.props.user.user}
                        <b className="caret"></b></a>
                    <ul className="dropdown-menu">
                        <li><a href={window.apiURLs.logout}>Log Out</a></li>
                    </ul>
                </li>
            )
        } else {
            return (
                <li className="active">
                    <form id="login-form" method="post" class="navbar-form navbar-left" action={window.apiURLs.login}>
                        <div method="post" className="navbar-form navbar-left">
                            <div className="form-group">
                                <input type="text"
                                       className="form-control" placeholder="Username" name="username"/>
                            </div>

                            <div className="form-group">
                                <input type="password"
                                       className="form-control" placeholder="Password" name="password"/>
                            </div>
                            <button onClick={this.props.login} className="btn btn-default">Login</button>
                        </div>
                    </form>
                </li>
            )
        }
    }
});

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}