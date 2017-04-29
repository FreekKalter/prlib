const ReactDataGrid = require('react-data-grid');
const ReactDOM = require('react-dom');
const React = require('react');
const update = require('immutability-helper');
const { Toolbar, Filters: { NumericFilter }, Data: { Selectors } } =  require('react-data-grid-addons');

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

const HumanReadableSizeFormatter = React.createClass({
  propTypes: {
      value: React.PropTypes.number.isRequired
  },

  render() {
    var bytes = this.props.value;
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
    return (<span>{ bytes.toFixed(1)+' '+units[u] }</span>);
  }
});

const Example = React.createClass({
  getInitialState() {
    this._columns = [
      {
        key: 'name',
        name: 'Name',
        width: 500,
        resizable: true,
        sortable: true,
        filterable: true
      },
      {
        key: 'size',
        name: 'Size',
        width: 100,
        sortable: true,
        resizable: true,
        filterable: true,
        filterRenderer: NumericFilter,
        formatter: HumanReadableSizeFormatter
      },
      {
        key: 'added',
        name: 'Added on',
        width: 200,
        resizable: true,
        sortable: true,
        filterable: true,
        formatter: DateFormatter,
      },
      {
        key: 'rating',
        name: 'Rating',
        width: 200,
        editable: true,
        resizable: true,
        sortable: true,
        filterable: true,
        filterRenderer: NumericFilter,
        formatter: RatingFormatter,
      }
    ];
    let rows = movies;
    return {rows, filters: {}};
  },

  getRows(){
    return Selectors.getRows(this.state);
  },

  rowGetter(i) {
      let rows= this.getRows();
      return rows[i];
  },

  getSize(){
    return this.getRows().length;
  },

  onClearFilters() {
    // all filters removed
    this.setState({filters: {} });
  },

  handleGridRowsUpdated({ fromRow, toRow, updated }) {
    let rows = this.state.rows;
    for (let i = fromRow; i <= toRow; i++) {
      let rowToUpdate = rows[i];
      let updatedRow = update(rowToUpdate, {$merge: updated});
      rows[i] = updatedRow;
    }
    this.setState({ rows });
  },


  handleFilterChange(filter) {
    let newFilters = Object.assign({}, this.state.filters);
    if (filter.filterTerm) {
      newFilters[filter.column.key] = filter;
    } else {
      delete newFilters[filter.column.key];
    }
    this.setState({ filters: newFilters });
  },

  handleGridSort(sortColumn, sortDirection) {
    const comparer = (a, b) => {
     if (sortDirection === 'ASC' || sortDirection ==='NONE') {
       return (a[sortColumn] > b[sortColumn]) ? 1 : -1;
     } else if (sortDirection === 'DESC') {
       return (a[sortColumn] < b[sortColumn]) ? 1 : -1;
     }
    };
    const rows = this.getRows().sort(comparer);
    this.setState({ rows });
  },

  render() {
    return  (
      <ReactDataGrid
        onGridSort={this.handleGridSort}
        columns={this._columns}
        rowGetter={this.rowGetter}
        enableCellSelect = {true}
        rowsCount={this.getSize()}
        onGridRowsUpdated={this.handleGridRowsUpdated}
        toolbar={<Toolbar enableFilter={true}/>}
        onAddFilter={this.handleFilterChange}
        onClearFilters={this.onClearFilters}
        minHeight={window.innerHeight - 100} />
    );
  }
});

ReactDOM.render(
  <Example />,
  document.getElementById('container')
);
