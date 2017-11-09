const React = require('react');
const HumanReadableSizeFormatter = require('./formatters/HumanReadableSizeFormatter.js');
const RatingFormatter = require('./formatters/RatingFormatter.js');

class SingleMOvieView extends React.Component{
    constructor(props){
        super(props);
        this.state = {name: '', rating: '', comment: '', tags: '', size: 0};

        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.handleDelete = this.handleDelete.bind(this);
    }

    componentDidMount(){
        var id = this.props.match.params.id;
        fetch('/movie/'+id).then(function(response){
            response.json().then(function(data){
                if(!data.rating){
                    data.rating = '';
                }
                this.setState(data);
            }.bind(this));
        }.bind(this));
    }

    handleSubmit(){
        fetch('/movie/'+this.state.id,
              { method: 'PUT', body: JSON.stringify(this.state)}
        ).then(function(response){
          console.log(response);
        });
    }

    handleSubmitAndBack(){
        this.handleSubmit();


    }

    handleChange(event){
        var id = event.target.id;
        this.setState({[id]: event.target.value});
    }

    handleDelete(){
        fetch('/movie/'+ this.state.id , {method: 'DELETE'}).then(function(response){
            response.json().then(function(data){
                //TODO: error handling
                console.log(data);
            })
        });
    }
    render(){
      return(
        <div>
            <form className="form-horizontal">
              <div className="form-group">
                <label htmlFor="name" className="col-sm-2 control-label">Name</label>
                <div className="col-sm-7">
                    <input type="text" className="form-control" id="name" value={this.state.name} onChange={this.handleChange}/>
                </div>
              </div>
              <div className="form-group">
                <label htmlFor="rating" className="col-sm-2 control-label">Rating</label>
                <div className="col-sm-2">
                    <input type="number" className="form-control" id="rating" value={this.state.rating} onChange={this.handleChange}/>
                </div>
                <div className="col-sm-5">
                    <RatingFormatter value={this.state.rating} />
                </div>
              </div>
              <div className="form-group">
                <label className="col-sm-2 control-label">Size</label>
                <div className="col-sm-7">
                    <p className="form-control-static"><HumanReadableSizeFormatter value={this.state.size} /></p>
                </div>
              </div>
              <div className="form-group">
                <label htmlFor="tags" className="col-sm-2 control-label">Tags</label>
                <div className="col-sm-7">
                    <input className="form-control" id="tags" value={this.state.tags} onChange={this.handleChange}/>
                </div>
              </div>
              <div className="form-group">
                <label htmlFor="comment" className="col-sm-2 control-label">Comment</label>
                <div className="col-sm-7">
                    <textarea className="form-control" rows="4" id="comment" value={this.state.comment} onChange={this.handleChange}/>
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="files" className="col-sm2 control-label">Files</label>
                <div className="col-sm-7">
                    <p className="form-control-static">{this.state.files}</p>
                </div>
              </div>

              <div className="form-group">
                <div className="col-sm-offset-2 col-sm-7">
                  <button type="button" onClick={this.handleSubmit} className="btn btn-default">Save</button>
                  <button type="button" onClick={this.handleSubmitAndBack} className="btn btn-default">Save and back</button>
                  <button type="button" onClick={this.handleDelete} className="btn btn-danger">Delete</button>
                </div>
              </div>
            </form>
        </div>
      );
    }

};

module.exports = SingleMOvieView;
