const ReactDataGrid = require('react-data-grid');
const ReactDOM = require('react-dom');
const React = require('react');
const update = require('immutability-helper');
const HumanReadableSizeFormatter = require('./formatters/HumanReadableSizeFormatter.js');
const RatingFormatter = require('./formatters/RatingFormatter.js');
const { Toolbar, Filters: { NumericFilter }, Data: { Selectors } } =  require('react-data-grid-addons');
import { Link } from 'react-router-dom';

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


const IDFormatter = React.createClass({
    propTypes:{
        value: React.PropTypes.number.isRequired
    },

    render(){
        var href = "/details/" + this.props.value;
        return(<Link to={href}>{this.props.value}</Link>)
    }
});

const EmptyRowsView = React.createClass({
    //TODO: little more responsive loading view
  render() {
    return (<div>Loading...</div>);
  }
});

const MovieGrid = React.createClass({
  getInitialState() {
    this._columns = [
      {
        key: 'id',
        name: 'Id',
        width: 50,
        formatter: IDFormatter
      },
      {
        key: 'name',
        name: 'Name',
        width: 500,
        editable: true,
        resizable: true,
        sortable: true,
        filterable: true
      },
      {
        key: 'size',
        name: 'Size',
        width: 150,
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
    let rows = [];
    return {rows, filters: {}};
  },

  componentDidMount(){
      fetch('/all_movies').then(function(response){
          response.json().then(function(data){
              this.setState({rows: data});
          }.bind(this));
      }.bind(this));
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
    this.sendVisibleList();
  },

  handleGridRowsUpdated({ fromRow, toRow, updated }) {
    let rows = this.state.rows;
    for (let i = fromRow; i <= toRow; i++) {
      let rowToUpdate = rows[i];
      let updatedRow = update(rowToUpdate, {$merge: updated});
      fetch('/movie/'+updatedRow['id'], { method: 'PUT', body: JSON.stringify(updatedRow)}).then(function(response){
      });
      rows[i] = updatedRow;
    }
    this.setState({ rows });
  },

  handleFilterChangeDelay(filter){
      clearTimeout(this.props.timerId);
      this.props= { timerId: setTimeout(this.handleFilterChange, 500, filter)};
  },

  handleFilterChange(filter) {
    let newFilters = Object.assign({}, this.state.filters);
    if (filter.filterTerm) {
      newFilters[filter.column.key] = filter;
    } else {
      delete newFilters[filter.column.key];
    }
    this.setState({ filters: newFilters });
    this.sendVisibleList();
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

  sendVisibleList(){
    fetch('/visible_ids', {method: 'POST', body: JSON.stringify(this.getRows())}).then(function(respons){});
  },

  renderButton(){
    return(<button type="button" className="btn" onClick={() => this.sendVisibleList() }>Send list</button>);
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
        toolbar={<Toolbar enableFilter={true} children={this.renderButton()} />}
        onAddFilter={this.handleFilterChangeDelay}
        onClearFilters={this.onClearFilters}
        emptyRowsView={EmptyRowsView}
        minHeight={window.innerHeight - 100} />
    );
  }
});

module.exports = MovieGrid;
