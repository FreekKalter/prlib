const React = require('react');

const RatingFormatter = React.createClass({
  createMarkup(){
    var value = this.props.value;
    if (typeof this.props.value =='string'){
        value = parseInt(this.props.value, 10);
    }
    var nrStars = Math.round(value/10);
    var output = [];
    for(var i=0; i<nrStars; i++){
        output.push('<span class="glyphicon glyphicon-star"> </span>');
    }
    for(var i=0; i<10-nrStars; i++){
        output.push('<span class="glyphicon glyphicon-star-empty"> </span>');
    }
    return {__html: output.join('')};
  },

  render(){
      return <div dangerouslySetInnerHTML={this.createMarkup()} />;
  }
});

module.exports = RatingFormatter;
