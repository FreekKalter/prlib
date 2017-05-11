const React = require('react');
const ReactDOM = require('react-dom');
const Carousel = require('nuka-carousel');
const MovieGrid = require('./MovieGrid.js');



class PreviewWindow extends React.Component {
    constructor(props){
        super(props);
        this.state = {images: [{thumbnail: "", preview: "", toShow: "placeholder.png"}]};
        this.handleMouseOver = this.handleMouseOver.bind(this);
        this.handleMouseOut = this.handleMouseOut.bind(this);
        this.RowSelect = this.RowSelect.bind(this);
    }

    handleMouseOver(event){
        var src = event.target.src.substring(event.target.src.lastIndexOf('/') + 1);
        var index = this.state.images.map(function(i){return i.thumbnail;}).indexOf(src);
        if(index >= 0){
            var images = this.state.images;
            // Cant asign directly to images[index] or someting in optimaztion gets lost
            // freaky bug somewhere in transpilin/compiling/building this whole mess
            var preview = images[index].preview;
            images[index].toShow = preview;
            this.setState({images:images});
        }
    }

    handleMouseOut(event){
        var src = event.target.src.substring(event.target.src.lastIndexOf('/') + 1);
        var index = this.state.images.map(function(i){return i.preview;}).indexOf(src);
        var images = this.state.images;
        if(index >= 0){
            // Cant asign directly to images[index] or someting in optimaztion gets lost
            // freaky bug somewhere in transpilin/compiling/building this whole mess
            var thumbnail = images[index].thumbnail;
            images[index].toShow = thumbnail;
            this.setState({images:images});
        }
    }

    prependLocation(img){
        return('/static/images/previews/' + img);
    }

    RowSelect(rowIdx, row){
        fetch('/get_files/' + row.id).then(function(response){
          response.json().then(function(data){
              var imagedict = {};
              for(var i=0; i< data.length; i++){
                  data[i].toShow = data[i].thumbnail;
              }
              this.setState({images: data});
          }.bind(this));
        }.bind(this));
    }

    render(){
        return(
                <div>
                    <MovieGrid onRowSelect={this.RowSelect}/>
                    <div>
                            <Carousel slideWidth="320px"
                                      cellAlign="left"
                                      cellSpacing={5}
                                      slidesToShow={4}>
                                {this.state.images.map((image) =>
                                    <img key={image.thumbnail} onMouseOver={this.handleMouseOver} onMouseOut={this.handleMouseOut}
                                         width="320px" height="180px" src={this.prependLocation(image.toShow)}/>
                                )}
                            </Carousel>
                    </div>
                </div>
              );
    }
}

ReactDOM.render(
  <PreviewWindow />,
  document.getElementById('container')
);
