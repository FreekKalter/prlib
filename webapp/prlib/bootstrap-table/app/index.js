var React = require('react');
var ReactDOM = require('react-dom');
var ReactBsTable  = require('react-bootstrap-table');
var BootstrapTable = ReactBsTable.BootstrapTable;
var TableHeaderColumn = ReactBsTable.TableHeaderColumn;


const options = {
    onRowClick: function(row){
        console.log(row);
    }
};


function HumanReadableSizeFormatter(cell, row){
    var bytes = cell;
    var si = true;
    var thresh = si ? 1000 : 1024;
    if(Math.abs(bytes) < thresh) {
        return bytes + ' B';
    }
    var units = si
        ? ['kB','MB','GB','TB','PB','EB','ZB','YB']
        : ['KiB','MiB','GiB','TiB','PiB','EiB','ZiB','YiB'];
    var u = -1;
    do {
        bytes /= thresh;
        ++u;
    } while(Math.abs(bytes) >= thresh && u < units.length - 1);
    return ( bytes.toFixed(1)+' '+units[u]);
}

function RatingFormatter(cell, row){
    var nrStars = Math.round(cell/10);
    var output = '';
    for(var i=0; i<nrStars; nrStars++){
        output += '<span class="glyphicon glyphicon-star"> </span>';
    }
    for(var i=0; i<10-nrStars; nrStars++){
        output += '<span class="glyphicon glyphicon-star-empty"> </span>';
    }
    return(output);
}

ReactDOM.render(
  <BootstrapTable data={movies} height={window.innerHeight - 10} options={options} striped hover>
      <TableHeaderColumn dataField='id' isKey hidden>ID</TableHeaderColumn>
      <TableHeaderColumn dataField='name'
                         dataSort={true}
                         filter={ {type: 'RegexFilter', delay: 1000} } >Name</TableHeaderColumn>
      <TableHeaderColumn dataField='size'
                         dataFormat={ HumanReadableSizeFormatter }
                         dataSort={true}
                         filter={ {
                            type: 'NumberFilter',
                            delay: 1000,
                            numberComparators: [ '>', '<' ]
                         } }
                         width='250'>Size</TableHeaderColumn>
      <TableHeaderColumn dataField='rating'
                         dataSort={true}
                         dataFormat={RatingFormatter}
                         filter={ {
                            type: 'NumberFilter',
                            delay: 1000,
                            numberComparators: [ '>', '<' ]
                         } }
                         width='250'>Rating</TableHeaderColumn>
  </BootstrapTable>,
  document.getElementById('container')
);
