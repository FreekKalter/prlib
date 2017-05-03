const React = require('react');
const ReactDOM = require('react-dom');
const MovieGrid = require('./MovieGrid.js');
const SingleMovieView = require('./SingleMovieView.js');
const RandomMovieView = require('./RandomMovieView.js');

import {
  BrowserRouter as Router,
  Route,
  Link
} from 'react-router-dom';

ReactDOM.render(
  <Router>
    <div>
        <Link to='/'><h1>MovieDB</h1></Link>
        <Link to='/random'>Random</Link>
        <Route exact path="/" component={MovieGrid}/>
        <Route path="/details/:id" component={SingleMovieView} />
        <Route path="/random" component={RandomMovieView} />
    </div>
  </Router>,
  document.getElementById('container')
);
