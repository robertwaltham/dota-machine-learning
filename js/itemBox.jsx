var ReactRouter = require('react-router');
var Router = ReactRouter.Router;
var Route = ReactRouter.Route;
var Link = ReactRouter.Link;
var History = ReactRouter.History;


module.exports = React.createClass({
    getInitialState: function () {
        return {data: []};
    },
    componentDidMount: function () {
        window.startLoading();
        $.ajax({
            url: window.apiURLs.itemList,
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
                <div key={item.item_id} className="col-md-1 col-sm-2">
                    <div className="item-image">
                        <Link to={`/Item/${item.item_id}`} params={{id:item.item_id}}>
                            <img src={item.image}/>
                        </Link>
                    </div>
                </div>
            );
        });
        return (
            <div className="row">
                {itemNodes}
            </div>
        );
    }
});
