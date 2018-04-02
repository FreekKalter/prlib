const ReactDataGrid = require('react-data-grid');
const React = require('react');

const update = require('immutability-helper');
const classNames = require('classnames');

const HumanReadableSizeFormatter = require('./formatters/HumanReadableSizeFormatter.js');
const RatingFormatter = require('./formatters/RatingFormatter.js');
const DateFormatter = require('./formatters/DateFormatter.js');

const { Toolbar, Filters: { NumericFilter, SingleSelectFilter, AutoCompleteFilter}, Data: { Selectors } } =  require('react-data-grid-addons');
const Modal = require('react-bootstrap/lib/Modal');
const Button = require('react-bootstrap/lib/Button');

const FileSizeFilter = require('./filters/FileSizeFilter.js');
const DateFilter = require('./filters/DateFilter.js');
import CompressedFilter from './filters/CompressedFilter.js';


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
                {this.props.value} <span style={{color: '#33a6d6'}} className="glyphicon glyphicon-play"></span>
            </button>
        </span>
      );
    }
}

class CompressedFormatter extends React.Component{
    constructor(props){
        super(props);
    }
    getStyle(){
        if(this.props.value == '✔'){
            return{color: 'green'}
        }else{
            return{color: '#f1204c'}
        }
    }
    render(){
        if(this.props.value == '✔'){
            return(<span style={this.getStyle()}>✔</span>);
        }else{
            return(<span style={this.getStyle()}>✘</span>);
        }
    }
}

const MovieGrid = React.createClass({
  getInitialState() {
    this._columns = [
      {
        key             : 'id',
        name            : 'Id',
        width           : 70,
        formatter       : IdFormatter
      },
      {
        key             : 'name',
        name            : 'Name',
        width           : 500,
        resizable       : true,
        sortable        : true,
        filterable      : true
      },
      {
        key             : 'size',
        name            : 'Size',
        width           : 150,
        sortable        : true,
        resizable       : true,
        filterable      : true,
        filterRenderer  : FileSizeFilter,
        formatter       : HumanReadableSizeFormatter
      },
      {
        key             : 'compressed',
        name            : <span className="glyphicon glyphicon-compressed"></span>,
        width           : 100,
        sortable        : true,
        resizable       : true,
        filterable      : true,
        filterRenderer  : CompressedFilter,
        formatter       : CompressedFormatter
      },
      {
        key             : 'nr_files',
        name            : 'Nr of files',
        width           : 100,
        sortable        : true,
        resizable       : true,
        filterable      : true,
        filterRenderer  : NumericFilter,
      },
      {
        key             : 'added',
        name            : 'Added on',
        width           : 180,
        resizable       : true,
        sortable        : true,
        filterable      : true,
        filterRenderer  : DateFilter,
        formatter       : DateFormatter,
      },
      {
        key             : 'last_played',
        name            : 'Last played',
        width           : 180,
        resizable       : true,
        sortable        : true,
        filterable      : true,
        filterRenderer  : DateFilter,
        formatter       : DateFormatter,
      },
      {
        key             : 'tags',
        name            : 'Tags',
        width           : 190,
        editale         : false,
        resizable       : true,
        filterable      :true,
      },
      {
        key             : 'rating',
        name            : 'Rating',
        width           : 200,
        editable        : true,
        resizable       : true,
        sortable        : true,
        filterable      : true,
        filterRenderer  : NumericFilter,
        formatter       : RatingFormatter,
      }

      //TODO: column with Series this movie belongs to
    ];
    let rows = [];
    return {rows: rows, filters: {}, selectedModal: {name: "testing", files: []}, showModal: false, modal_title: '', tagInput: ''};
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
    this.setState({filters: {}, rows: this.state.rows.slice() });
    setTimeout(this.sendVisibleList, 400);
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

  getValidFilterValues(columnId) {
      let values = this.state.rows.map(r => r[columnId]);
      return values.filter((item, i, a) => { return i === a.indexOf(item); });
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

  handleRowClick(rowIdx, row){
      if(row){
          this.setState({selectedModal: row});
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
      console.log(this.state.selectedModal);
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
      this.setState({rows: this.state.rows.slice()});
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
              this.state.rows.splice(i, 1)
              break;
          }
      }
      this.setState({rows: this.state.rows.slice()});
  },

  update_current_random(){
    fetch('/current_random').then(function(response){
        response.json().then(function(data){
            if (data.id != this.state.selectedModal.id){
                this.setState({selectedModal: data});
            }
        }.bind(this));
    }.bind(this));
  },

  handleCompress(){
    fetch('/compress', {method: 'POST', body: JSON.stringify(this.getRows())}).then(function(respons){});
  },

  handleCompressOne(){
    fetch('/compress', {method: 'POST', body: JSON.stringify([this.state.selectedModal])}).then(function(respons){});
    this.handleCloseModal();
  },

  renderRandomModal(){
    this.setState({modal_title: 'Random'});
    this.update_current_random();
    this.handleShowModal();
    this.timerId = setInterval( () => this.update_current_random(), 2300);
  },

  onRowSelect(rows){
    this.setState({ selectedRows: rows });
  },

  handleTagRows(){
    console.log(this.state.tagInput);
    fetch('/tagmultiple', {method: 'POST', body: JSON.stringify({rows: this.state.selectedRows, tag: this.state.tagInput})}).then(function(respons){});
    setTimeout(this.getMovies, 400);
  },

  // Toolbar buttons
  renderSendListButton(){
    return(<button type="button" className="btn" key="send" onClick={() => this.sendVisibleList() }><span className="glyphicon glyphicon-transfer"></span> Send list</button>);
  },

  renderRandomButton(){
    return(<button type="button" className="btn" key="random" onClick={() => this.renderRandomModal() }><span className="glyphicon glyphicon-random"></span> Random</button>);
  },

  renderRefreshButton(){
    return(<button type="button" className="btn btn-default" key="refresh" onClick={() => this.getMovies() }><span className="glyphicon glyphicon-refresh"></span> Refresh</button>);
  },

  renderRescanButton(){
    return(<button type="button" className="btn" key="rescan" onClick={
        () => fetch('/scan_dir').then(function(response){})}><span className="glyphicon glyphicon-search"></span> Rescan</button>);
  },

  renderRepairButton(){
    return(<button type="button" className="btn" key="repair" onClick={
        () => fetch('/repair').then(function(response){})}><span className="glyphicon glyphicon-wrench"></span> Repair</button>);
  },

  renderCompressButton(){
    return(<button type="button" className="btn btn-default" key="compress" onClick={() => this.handleCompress() }><span className="glyphicon glyphicon-compressed"></span> Compress</button>);
  },

  renderTagButton(){
    return(<button type="button" className="btn btn-default" key="tag" onClick={() => this.handleTagRows() }><span className="glyphicon glyphicon-tag"></span> Tag</button>);
  },

  renderTagInput(){
    return(<input type="text" value={this.state.tagInput} key="taginput" onChange={this.tagInputChange}/>);
  },

  renderItemCount(){
    return(<span key="itemcount">{this.getSize()}</span>);
  },

  tagInputChange(event){
      this.setState({tagInput: event.target.value});
  },

  render() {
    return  (
      <div>
        <ReactDataGrid
          onGridSort={this.handleGridSort}
          columns={this._columns}
          rowGetter={this.rowGetter}
          rowsCount={this.getSize()}
          toolbar={<Toolbar enableFilter={true}
                            children={[this.renderItemCount(),
                                       this.renderSendListButton(),
                                       this.renderRandomButton(),
                                       this.renderRescanButton(),
                                       this.renderRepairButton(),
                                       this.renderRefreshButton(),
                                       this.renderCompressButton(),
                                       this.renderTagButton(),
                                       this.renderTagInput()]} />}
          onAddFilter={this.handleFilterChangeDelay}
          onClearFilters={this.onClearFilters}
          getValidFilterValues={this.getValidFilterValues}
          emptyRowsView={EmptyRowsView}
          onRowClick={this.handleRowClick}
          minHeight={window.innerHeight - 250}
          enableRowSelect="multi"
          onRowSelect={this.onRowSelect}

          />

        <Modal bsSize="large" animation={false} show={this.state.showModal} onHide={this.handleCloseModal}>
          <Modal.Header closeButton>
            <Modal.Title>{this.state.modal_title}</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <form className="form-horizontal">
              <div className="form-group">
                <label htmlFor="name" className="col-sm-2 control-label">Name</label>
                <div className="col-sm-8">
                    <input type="text" className="form-control" id="name" value={this.state.selectedModal.name} onChange={this.handleChange}/>
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="rating" className="col-sm-2 control-label">Rating</label>
                <div className="col-sm-3">
                    <input type="number" className="form-control" id="rating" value={this.state.selectedModal.rating} onChange={this.handleChange}/>
                </div>
                <div className="col-sm-5">
                    <RatingFormatter value={this.state.selectedModal.rating} />
                </div>
              </div>

              <div className="form-group">
                <label className="col-sm-2 control-label">Size</label>
                <div className="col-sm-8">
                    <p className="form-control-static"><HumanReadableSizeFormatter value={this.state.selectedModal.size} /></p>
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="tags" className="col-sm-2 control-label">Tags</label>
                <div className="col-sm-8">
                    <input className="form-control" id="tags" value={this.state.selectedModal.tags} onChange={this.handleChange}/>
                </div>
              </div>
              <div className="form-group">
                <label htmlFor="comment" className="col-sm-2 control-label">Comment</label>
                <div className="col-sm-8">
                    <textarea className="form-control" rows="4" id="comment" value={this.state.selectedModal.comment} onChange={this.handleChange}/>
                </div>
              </div>

              <div className="form-group">
                <label className="col-sm-2 control-label">Size</label>
                <div className="col-sm-6">
                    <ul className="modalFileList">
                        {this.state.selectedModal.files.map((item, index) => (
                            <li key={index}>{item[0]}</li>
                        ))}
                    </ul>
                </div>
                <div className="col-sm-2">
                    <ul className={classNames("modalSizeList", "text-right")}>
                        {this.state.selectedModal.files.map((item, index) => (
                            <li key={index}><HumanReadableSizeFormatter value={item[1]} /></li>
                        ))}
                    </ul>
                </div>
              </div>

              <div className="form-group">
                <div className="col-sm-offset-2 col-sm-7">
                  <button type="button" onClick={this.handleSave} className="btn btn-default">Save</button>
                  <button type="button" onClick={this.handleSaveAndClose} className="btn btn-default">Save and close</button>
                  <button type="button" onClick={this.handleCompressOne} className="btn btn-primary">Compress</button>
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
