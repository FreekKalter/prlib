const React = require('react');
const ReactDOM = require('react-dom');
const MovieGrid = require('./MovieGrid.js');

ReactDOM.render(
    <div>
        <h1>MovieDB</h1>
        <MovieGrid />
    </div>,
  document.getElementById('container')
);
