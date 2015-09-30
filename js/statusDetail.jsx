var StatusGraph = require('./statusGraph.jsx');

module.exports = React.createClass({
  getInitialState: function () {
    return {days: false}
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
    if (this.state.days) {
      return (
        <div>
          <div className="row">
            <div className="col-md-12">
              <h1> Status </h1>
            </div>
          </div>
          <div className="row">
            <div className="col-md-12">
              <h3> Matches By Date </h3>
            </div>
          </div>
          <div className="row">
            <div className="col-md-12">
              <StatusGraph data={this.state.days}/>
            </div>
          </div>

        </div>
      )
    } else {
      return (<div></div>);
    }

  }
});
