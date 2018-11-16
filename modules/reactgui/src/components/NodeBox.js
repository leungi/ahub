import React from 'react';
import {get} from '../modules/fetch';

const API_ENDPOINT = 'http://ahub.westeurope.cloudapp.azure.com:8000/';
//const API_ENDPOINT = 'http://127.0.0.1:8000/';

export default class NodeBox extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            response: "INIT",
            endpoints: [],
        };

        this.getEndpoints = this.getEndpoints.bind(this);
        this.getEndpointResponse = this.getEndpointResponse.bind(this);
    }

    componentDidMount () {
        this.getEndpoints();
    }

    getEndpoints() {
        /* get(`${API_ENDPOINT}${this.props.name}/endpoints`).then(endpoints => this.setState({
            endpoints,
        })).catch(err => console.warn(err)); */
        this.setState({
            endpoints: [
                {
                    name: 'batch',
                    response: {},
                }
            ]
        });
    }

    getEndpointResponse(endpointName) {
        get(`${API_ENDPOINT}${this.props.name}/${endpointName}`)
        //  get(`${API_ENDPOINT}${endpointName}`)
            .then(response => {
                const newEndpointState = [
                    ...this.state.endpoints,
                    {
                        name: endpointName,
                        response,
                    }
                ];

                this.setState({
                    endpoints: newEndpointState,
                });
            })
            .catch(err => console.warn(err));
    }

    render(){
        return(
            <div className="nodebox w3-col m4 l3">
                <div className="boxheader">
                    {this.props.name}
                </div>
                {
                    this.state.endpoints
                    ? this.state.endpoints.map(endpoint => (
                        <EndpointBox
                            key={`${this.props.name}-endpoint-${endpoint.name}`}
                            name={endpoint.name}
                            response={endpoint.response}
                            getEndpointResponse={this.getEndpointResponse}
                        />
                    ))
                    : <p>Loading endpoint functions...</p>
                }
            </div>
        )
    }
}

const EndpointBox = props => {
    return (
        <div className="boxbody">
            <button
                className="endpointbutton"
                onClick={() => props.getEndpointResponse(props.name)}>
                {props.name.toUpperCase()}
            </button>
            <div className="response">
                {JSON.stringify(props.response)}
            </div>
        </div>
    )
};
