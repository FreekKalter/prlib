const React = require('react');
const ReactDOM = require('react-dom');
const MovieGrid = require('./MovieGrid.js');

class PreviewWindow extends React.Component {
    constructor(props){
        super(props);
        this.state = {images: [{thumbnail: "", preview: "", toShow: "placeholder.png"}]};
        this.handleMouseOver = this.handleMouseOver.bind(this);
        this.handleMouseOut = this.handleMouseOut.bind(this);
        this.RowSelect = this.RowSelect.bind(this);
    }

    componentDidMount(){
        this.setState({rendered_images: this.render_images()});
    }

    handleMouseOver(event){
        var images = this.state.images;
        for(var i =0; i< images.length; i++){
            if(event.target.src.endsWith(images[i].thumbnail)){
                images[i].toShow = images[i].preview;
            }
        }
        this.setState({images: images});
        this.setState({rendered_images:this.render_images()});
    }

    handleMouseOut(event){
        var images = this.state.images;
        for(var i =0; i< images.length; i++){
            if(event.target.src.endsWith(images[i].preview)){
                images[i].toShow = images[i].thumbnail;
            }
        }
        this.setState({images: images});
        this.setState({rendered_images:this.render_images()});
    }

    prependLocation(img){
        if(img == 'placeholder.png'){
            return('/static/images/' + img);
        }
        return('/static/images/previews/' + img);
    }

    RowSelect(rowIdx, row){
        fetch('/get_files/' + row.id).then(function(response){
          response.json().then(function(data){
              //this.setState({thumbnail: data[0].thumbnail, preview: data[0].preview, toShow: this.prependLocation(data[0].thumbnail)});
              for(var i=0; i< data.length; i++){
                  data[i].toShow = data[i].thumbnail;
              }
              this.setState({images: data})
              this.setState({rendered_images:this.render_images()});
          }.bind(this));
        }.bind(this));
    }

    render_images(){
        return(this.state.images.map( (image) =>
                <img height="200px"
                     key={this.prependLocation(image.thumbnail)}
                     src={this.prependLocation(image.toShow)}
                     onMouseOver={this.handleMouseOver}
                     onMouseOut={this.handleMouseOut}>
                     </img> ));
    }
    render(){
        return(
                <div>
                    <MovieGrid onRowSelect={this.RowSelect}/>
                    <div id="preview">
                        {this.state.rendered_images}
                    </div>
                </div>
              );
    }
}

ReactDOM.render(
    <div>
        <PreviewWindow />
    </div>,
  document.getElementById('container')
);
