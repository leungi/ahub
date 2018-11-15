

import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';


// ========================================



class AhubGUI extends React.Component {
  render(){
    return(
      <div className="w3-row">
        <NodeBox name="node1"/>
        <NodeBox name="node2"/>
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
      <div className="nodebox w3-col m4 l3">
        <div className="boxheader">
          {this.props.name}
        </div>
        <div className="boxbody">
          <button
            className="endpointbutton"
            onClick={() => this.setState({response:
                triggerEndpoint(this.props.name, "batch")}
              )}>
            GET
          </button>
          <div className="response">
            {this.state.response}
          </div>
        </div>
      </div>
    )
  }
}
// ========================================

ReactDOM.render(
  <AhubGUI />,
  document.getElementById('root')
);


function triggerEndpoint(nodename, funcname) {
    var url = "http://ahub.westeurope.cloudapp.azure.com:8000/" +
      nodename + "/" + funcname
    return(
      url
      // instead run GET Request on above URL
    )
}
