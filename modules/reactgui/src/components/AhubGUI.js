import React from 'react';
import {get} from '../modules/fetch';
import NodeBox from './NodeBox';

const API_ENDPOINT = 'http://ahub.westeurope.cloudapp.azure.com:8000/';

export default class AhubGUI extends React.Component {
    constructor (props) {
        super(props);
        this.state = {
            nodes: []
        };
    }

    componentDidMount () {
        get(`${API_ENDPOINT}boss/get_services`)
            .then(response => this.setState({nodes: response.apis}))
            .catch(err => {
                console.warn(err);
                // prefill nodes for testing purposes
                this.setState({nodes: ['node1', 'node2']});
            });
    }

    render(){
        return(
            <div className="w3-row">
                {
                    this.state.nodes
                    ? this.state.nodes.map(node => <NodeBox key={`node-${node}`} name={node} />)
                    : <p>Loading nodes...</p>
                }
            </div>
        )
    }
}
