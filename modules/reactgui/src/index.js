

import 'bootstrap/dist/css/bootstrap.min.css';
import $ from 'jquery';
//import Popper from 'popper.js';
import 'bootstrap/dist/js/bootstrap.bundle.min';

import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';

// ========================================

class AhubGUI extends React.Component {
  render(){
    return(
      <div className="wrapper">
        <nav id="sidebar">
        <div className="sidebar-header">
          <h3>Bootstrap Sidebar</h3>
      </div>

      <ul className="list-unstyled components">
          <p>Dummy Heading</p>
          <li className="active">
              <a href="#homeSubmenu" data-toggle="collapse" aria-expanded="false" className="dropdown-toggle">Home</a>
              <ul className="collapse list-unstyled" id="homeSubmenu">
                  <li>
                      <a href="#">Home 1</a>
                  </li>
                  <li>
                      <a href="#">Home 2</a>
                  </li>
                  <li>
                      <a href="#">Home 3</a>
                  </li>
              </ul>
          </li>
          <li>
              <a href="#">About</a>
          </li>
          <li>
              <a href="#pageSubmenu" data-toggle="collapse" aria-expanded="false" className="dropdown-toggle">Pages</a>
              <ul className="collapse list-unstyled" id="pageSubmenu">
                  <li>
                      <a href="#">Page 1</a>
                  </li>
                  <li>
                      <a href="#">Page 2</a>
                  </li>
                  <li>
                      <a href="#">Page 3</a>
                  </li>
              </ul>
          </li>
          <li>
              <a href="#">Portfolio</a>
          </li>
          <li>
              <a href="#">Contact</a>
          </li>
      </ul>

        </nav>
        <nav id = "content">
          <div className="w3-row">
            <NodeBox name="node1"/>
            <NodeBox name="node2"/>
          </div>
          </nav>
        </div>
    )
  }
}

class NodeBox extends React.Component {
  constructor(props) {
    super(props);
    this.name = null;
    this.state = {
      response: "INIT"
    };
  }

  render(){
    return(

          <div className="nodebox w3-col">
            <div className="boxheader">
              {this.props.name}
            </div>
            <div className="boxbody">
              <button
                className="endpointbutton"
                onClick={() => this.triggerEndpoint(this.props.name, "batch")}>
                GET
              </button>
              <div className="response">
                {this.state.response}
              </div>
            </div>
          </div>

    )
  }

  triggerEndpoint(nodename, funcname) {
      var url = "https://ahub@ilikebigwhales:ahub.westeurope.cloudapp.azure.com/" +
        nodename + "/" + funcname
      $.getJSON(url, function(data) {this.setresponse(data)});
      return(
        "TEST"// instead run GET Request on above URL
      )
  }

  setresponse(data){
    this.setState({response: data})
  }

}
// ========================================

ReactDOM.render(
  //<ThemeSwitcher/>,
  <AhubGUI />,
  document.getElementById('root')
);
