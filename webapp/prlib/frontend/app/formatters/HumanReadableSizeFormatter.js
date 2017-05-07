const React = require('react');

const HumanReadableSizeFormatter = React.createClass({
  render() {
    var bytes = this.props.value;
    var si = true;
    var thresh = si ? 1000 : 1024;
    if(Math.abs(bytes) < thresh) {
        return (<span>{bytes + ' B'}</span>);
    }
    var units = si
        ? ['kB','MB','GB','TB','PB','EB','ZB','YB']
        : ['KiB','MiB','GiB','TiB','PiB','EiB','ZiB','YiB'];
    var u = -1;
    do {
        bytes /= thresh;
        ++u;
    } while(Math.abs(bytes) >= thresh && u < units.length - 1);
    return (<span>{ bytes.toFixed(1)+' '+units[u] }</span>);
  }
});

module.exports = HumanReadableSizeFormatter;
