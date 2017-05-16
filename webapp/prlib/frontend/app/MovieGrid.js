const ReactDataGrid = require('react-data-grid');
const ReactDOM = require('react-dom');
const React = require('react');
const update = require('immutability-helper');
const HumanReadableSizeFormatter = require('./formatters/HumanReadableSizeFormatter.js');
const RatingFormatter = require('./formatters/RatingFormatter.js');
const DateFormatter = require('./formatters/DateFormatter.js');
const { Toolbar, Filters: { NumericFilter }, Data: { Selectors } } =  require('react-data-grid-addons');
const Modal = require('react-bootstrap/lib/Modal');
const Button = require('react-bootstrap/lib/Button');
const FileSizeFilter = require('./filters/FileSizeFilter.js');
const DateFilter = require('./filters/DateFilter.js');


const EmptyRowsView = React.createClass({
    //TODO: little more responsive loading view
  render() {
    return (<div>Loading...</div>);
  }
});

class IdFormatter extends React.Component{
    constructor(props){
        super(props);
        this.clickHandler = this.clickHandler.bind(this);
    }

    clickHandler(){
        fetch('/play/' + this.props.value).then(function(response){});
    }

    render(){
        return(
                <span>
                    <button type="button" className="btn btn-default btn-sm" onClick={this.clickHandler}>
                        {this.props.value} <span className="glyphicon glyphicon-play"></span>
                    </button>
                </span>
              );
    }
}


const MovieGrid = React.createClass({
  getInitialState() {
    this._columns = [
      {
        key: 'id',
        name: 'Id',
        width: 70,
        formatter: IdFormatter
      },
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
        width: 150,
        sortable: true,
        resizable: true,
        filterable: true,
        filterRenderer: FileSizeFilter,
        formatter: HumanReadableSizeFormatter
      },
      {
        key: 'nr_files',
        name: 'Nr of files',
        width: 100,
        sortable: true,
        resizable: true,
        filterable: true,
        filterRenderer: NumericFilter,
      },
      {
        key: 'added',
        name: 'Added on',
        width: 180,
        resizable: true,
        sortable: true,
        filterable: true,
        filterRenderer: DateFilter,
        formatter: DateFormatter,
      },
      {
        key: 'last_played',
        name: 'Last played',
        width: 180,
        resizable: true,
        sortable: true,
        filterable: true,
        filterRenderer: DateFilter,
        formatter: DateFormatter,
      },
      {
        key: 'tags',
        name: 'Tags',
        width: 200,
        editale: false,
        resizable: true,
        filterable:true,
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

      //TODO: column with number of files belonging to this movie
      //TODO: column with Series this movie belongs to
    ];
    let rows = [];
    return {rows: rows, filters: {}, selectedModal: {name: "testing"}, showModal: false, modal_title: ''};
  },

  getMovies(){
      fetch('/all_movies').then(function(response){
          response.json().then(function(data){
              this.setState({rows: data});
          }.bind(this));
      }.bind(this));
  },

  componentDidMount(){
      this.getMovies();
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
    this.setState({rows: rows});
  },

  sendVisibleList(){
    fetch('/visible_ids', {method: 'POST', body: JSON.stringify(this.getRows())}).then(function(respons){});
  },

  renderButton(){
    return(<button type="button" className="btn" key="send" onClick={() => this.sendVisibleList() }>Send list</button>);
  },

  handleRowClick(rowIdx, row){
      if(row){
          this.setState({selectedModal: row});
          //this.handleShowModal();
          this.props.onRowSelect(rowIdx, row, this.handleShowDetailsModal);
      }
  },

  handleCloseModal(){
      this.setState({showModal: false});
      clearInterval(this.timerId);
  },

  handleShowDetailsModal(){
      this.setState({modal_title: 'Details'});
      this.handleShowModal();
  },

  handleShowModal(){
      this.setState({showModal: true});
  },

  handleSave(){
      fetch('/movie/'+this.state.selectedModal.id,
            { method: 'PUT', body: JSON.stringify(this.state.selectedModal)}
      ).then(function(response){
      });
      for( let i=0; i< this.state.rows.length; i++ ){
          if(this.state.rows[i].id == this.state.selectedModal.id ){
              this.state.rows[i] = this.state.selectedModal;
          }
      }
  },

  handleSaveAndClose(){
      this.handleSave();
      this.handleCloseModal();
  },

  handleChange(event){
      var edited = {};
      for (var attr in this.state.selectedModal){
          edited[attr] = this.state.selectedModal[attr];
      }
      edited[event.target.id] = event.target.value;
      this.setState({selectedModal: edited});
  },

  handleDelete(){
      fetch('/movie/'+ this.state.selectedModal.id , {method: 'DELETE'}).then(function(response){
          response.json().then(function(data){
              //TODO: error handling
          }.bind(this))
      }.bind(this));
      this.handleCloseModal();
      var index;
      for( let i=0; i< this.state.rows.length; i++ ){
          if(this.state.rows[i].id == this.state.selectedModal.id ){
              index = i;
              break;
          }
      }
      this.state.rows.splice(index,1);

  },

  update_current_random(){
    fetch('/current_random').then(function(response){
        response.json().then(function(data){
            if(!data.rating){
                data.rating = '';
            }
            if (data.id != this.state.selectedModal.id){
                this.setState({selectedModal: data});
            }
        }.bind(this));
    }.bind(this));
  },

  renderRandomModal(){
    this.setState({modal_title: 'Random'});
    this.update_current_random();
    this.handleShowModal();
    this.timerId = setInterval( () => this.update_current_random(), 2300);
  },

  renderRandomButton(){
    return(<button type="button" className="btn" key="random" onClick={() => this.renderRandomModal() }>Random</button>);
  },

  renderRefreshButton(){
    return(<button type="button" className="btn btn-default" key="refresh" onClick={() => this.getMovies() }><span className="glyphicon glyphicon-refresh"></span> Refresh</button>);
  },

  renderRescanButton(){
    return(<button type="button" className="btn" key="rescan" onClick={
        () => fetch('/scan_dir').then(function(response){})}>Rescan</button>);
  },

  render() {
    return  (
      <div>
        <ReactDataGrid
          onGridSort={this.handleGridSort}
          columns={this._columns}
          rowGetter={this.rowGetter}
          rowsCount={this.getSize()}
          toolbar={<Toolbar enableFilter={true} children={[this.renderButton(), this.renderRandomButton(), this.renderRescanButton(), this.renderRefreshButton()]} />}
          onAddFilter={this.handleFilterChangeDelay}
          onClearFilters={this.onClearFilters}
          emptyRowsView={EmptyRowsView}
          onRowClick={this.handleRowClick}
          minHeight={window.innerHeight - 250}
          />

        <Modal bsSize="large" animation={false} show={this.state.showModal} onHide={this.handleCloseModal}>
          <Modal.Header closeButton>
            <Modal.Title>{this.state.modal_title}</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <form className="form-horizontal">
              <div className="form-group">
                <label htmlFor="name" className="col-sm-2 control-label">Name</label>
                <div className="col-sm-7">
                    <input type="text" className="form-control" id="name" value={this.state.selectedModal.name} onChange={this.handleChange}/>
                </div>
              </div>
              <div className="form-group">
                <label htmlFor="rating" className="col-sm-2 control-label">Rating</label>
                <div className="col-sm-2">
                    <input type="number" className="form-control" id="rating" value={this.state.selectedModal.rating} onChange={this.handleChange}/>
                </div>
                <div className="col-sm-5">
                    <RatingFormatter value={this.state.selectedModal.rating} />
                </div>
              </div>
              <div className="form-group">
                <label className="col-sm-2 control-label">Size</label>
                <div className="col-sm-7">
                    <p className="form-control-static"><HumanReadableSizeFormatter value={this.state.selectedModal.size} /></p>
                </div>
              </div>
              <div className="form-group">
                <label htmlFor="tags" className="col-sm-2 control-label">Tags</label>
                <div className="col-sm-7">
                    <input className="form-control" id="tags" value={this.state.selectedModal.tags} onChange={this.handleChange}/>
                </div>
              </div>
              <div className="form-group">
                <label htmlFor="comment" className="col-sm-2 control-label">Comment</label>
                <div className="col-sm-7">
                    <textarea className="form-control" rows="4" id="comment" value={this.state.selectedModal.comment} onChange={this.handleChange}/>
                </div>
              </div>

              <div className="form-group">
                <div className="col-sm-offset-2 col-sm-7">
                  <button type="button" onClick={this.handleSave} className="btn btn-default">Save</button>
                  <button type="button" onClick={this.handleSaveAndClose} className="btn btn-default">Save and close</button>
                  <button type="button" onClick={this.handleDelete} className="btn btn-danger">Delete</button>
                </div>
              </div>
            </form>
          </Modal.Body>
          <Modal.Footer>
            <Button onClick={this.handleCloseModal}>Close</Button>
          </Modal.Footer>
        </Modal>
      </div>
    );
  }
});

module.exports = MovieGrid;
