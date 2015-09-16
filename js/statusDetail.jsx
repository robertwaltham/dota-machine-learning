module.exports = React.createClass({
    getInitialState: function () {
        return {days: []}
    },
    componentDidMount: function () {
        window.startLoading(1);
        // load matches
        $.ajax({
            url: window.apiURLs.matchcreatedbydate,
            dataType: 'json',
            cache: false,
            success: function (data) {
                this.setState({days: data});
                window.finishLoading();
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(this.props.url, status, err.toString());
                window.finishLoading();
            }.bind(this)
        });
    },
    render: function () {
        if (window.logged_in_user) {
            var rows = this.state.days.map(function (day) {
                return (
                    <div key={day.date} className="row">
                        <div className="col-md-6">
                            {day.date}
                        </div>
                        <div className="col-md-6">
                            {day.count}
                        </div>
                    </div>
                )
            });
            return (
                <div>
                    <div className="row">
                        <div className="col-md-12">
                            <h1> Status and Administration </h1>
                        </div>
                    </div>
                    <div className="row">
                        <div className="col-md-12">
                            <h3> Matches By Date </h3>
                        </div>
                    </div>
                    <div className="row">
                        <div className="col-md-12">
                            {rows}
                        </div>
                    </div>
                </div>
            )
        } else {
            return (<div></div>);
        }

    }
});
