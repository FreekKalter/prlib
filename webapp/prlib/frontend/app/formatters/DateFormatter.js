const React = require('react');

const DateFormatter = React.createClass({
    format_time(date, secs){
      var hours = date.getHours();
      var minutes = "0" + date.getMinutes();
      var seconds = "0" + date.getSeconds();
      var formatted =  hours + ':' + minutes.substr(-2);
      if(secs){
          formatted += ':' + seconds.substr(-2);
      }
      return(formatted);
    },

    render(){
        var today = new Date();
        var date = new Date(this.props.value * 1000);
        if(today.getFullYear() == date.getFullYear() &&
           today.getMonth() == date.getMonth() &&
           today.getDate() == date.getDate()){
          return(<span>today at {this.format_time(date, true)}</span>);
        }else{
          var day = "0" + date.getDate();
          var month = "0" + date.getMonth();
          var year = date.getFullYear();
          var formattedDate = day.substr(-2) + '-' + month.substr(-2) + '-' + year;
          return(<span> {formattedDate} at {this.format_time(date, false)}</span>);
        }
    }
});

module.exports = DateFormatter;
