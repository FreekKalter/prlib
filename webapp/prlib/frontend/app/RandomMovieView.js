const React = require('react');
const SingleMovieView = require('./SingleMovieView.js')

class RandomMovieView extends SingleMovieView{
    constructor(props){
        super(props);
    }

    update_current_random(){
        var id;
        fetch('/current_random').then(function(response){
            response.json().then(function(data){
                id = data;
                console.log(id);
                fetch('/movie/'+id).then(function(response){
                    response.json().then(function(data){
                        if(!data.rating){
                            data.rating = '';
                        }
                        this.setState(data);
                    }.bind(this));
                }.bind(this));
            }.bind(this));
        }.bind(this));
    }

    tick(){
        this.update_current_random();
    }

    componentDidMount(){
        this.update_current_random();
        this.timerId = setInterval(
          () => this.tick(),
          2300
        );
    }

    componentWillUnmount(){
        clearInterval(this.timerId);
    }
};

module.exports = RandomMovieView;
