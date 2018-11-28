import React from 'react';
import {
    Box,
    Button,
    Heading,
    Paragraph,
    Text,
    FormField,
    TextInput,
} from 'grommet';
import {get} from '../modules/fetch';
import JSONPretty from 'react-json-pretty';
import 'react-json-pretty/JSONPretty.monikai.styl';

const API_ENDPOINT = 'http://ahub.westeurope.cloudapp.azure.com:8000/';
//const API_ENDPOINT = 'http://127.0.0.1:8000/';

export default class NodeBox extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            response: 'INIT',
            endpoints: {},
        };

        this.getEndpoints = this.getEndpoints.bind(this);
        this.getEndpointResponse = this.getEndpointResponse.bind(this);
        this.updateEndpointQuery = this.updateEndpointQuery.bind(this);
    }

    componentDidMount() {
        this.getEndpoints();
    }

    getEndpoints() {
        get(`${API_ENDPOINT}${this.props.name}/swagger.json`)
            .then(response => {
                console.log(response);

                const endpoints = Object.keys(response.paths).reduce((endpoints, endpoint) => {
                        endpoints[endpoint] = {
                            response: null,
                            params: response.paths[endpoint].get.parameters,
                        };
                        return endpoints;
                    }, {});

                this.setState({
                    endpoints,
                });
            })
            .catch(err => console.warn(err));

    }

    updateEndpointQuery(endpointName, queryParam) {
        return event => {
            this.setState({
                endpoints: {
                    ...this.state.endpoints,
                    [endpointName]: {
                        ...this.state.endpoints[endpointName],
                        query: {
                            ...this.state.endpoints[endpointName].query,
                            [queryParam]: event.target.value,
                        }
                    }
                }
            })
        }
    }

    getEndpointResponse(endpointName) {
        let queryPartsString = '';

        if(this.state.endpoints[endpointName].query) {
            queryPartsString = Object.entries(this.state.endpoints[endpointName].query)
                .reduce((queryString, queryParts, index) => {
                    if (queryParts[1]) {
                        queryString += `${index > 0 ? '&' : '?'}${queryParts[0]}=${queryParts[1]}`;
                    }
                    return queryString;
                }, '');
        }

        get(`${API_ENDPOINT}${this.props.name}/${endpointName}${queryPartsString}`)
        //  get(`${API_ENDPOINT}${endpointName}`)
            .then(response => {
                const newEndpointState = {
                    ...this.state.endpoints,
                    [endpointName]: {
                        ...this.state.endpoints[endpointName],
                        response,
                    }
                };

                this.setState({
                    endpoints: newEndpointState,
                });
            })
            .catch(err => console.warn(err));
    }

    render() {
        return (
            <Box
                margin={{
                    horizontal: 'medium'
                }}
                pad='medium'
            >
                <Heading level='2'>
                    Overview for: <Text color='accent-1' size='xxlarge'>{this.props.name}</Text>
                </Heading>
                {
                    this.state.endpoints
                        ? Object.keys(this.state.endpoints).map(endpoint => (
                            <EndpointBox
                                key={`${this.props.name}-endpoint-${endpoint}`}
                                name={endpoint}
                                queryParameters={this.state.endpoints[endpoint].params}
                                updateEndpointQuery={this.updateEndpointQuery}
                                response={this.state.endpoints[endpoint].response}
                                getEndpointResponse={this.getEndpointResponse}
                            />
                        ))
                        : <Paragraph>Loading endpoint functions...</Paragraph>
                }
            </Box>
        );
    }
}


const EndpointBox = ({
    name,
    response,
    queryParameters,
    getEndpointResponse,
    updateEndpointQuery,
}) => {
    return (
        <Box
            basis='auto'
            border='all'
            margin={{
                vertical: 'medium'
            }}
            pad='medium'
            background='neutral-1'
            fill={false}
        >
            {queryParameters && queryParameters.map(param => (
                <FormField
                    label={`${param.name} (${param.description})`}
                    htmlFor={`input-${param.name}`}
                    key={`${name}-input-${param.name}`}
                >
                    <TextInput
                        id={`input-${param.name}`}
                        placeholder={param.name}
                        onChange={updateEndpointQuery(name, param.name)}
                    />
                </FormField>
            ))}
            <Button
                className='endpointbutton'
                onClick={() => getEndpointResponse(name)}
                label={name.toUpperCase()}
            />
            {
                response &&
                <JSONPretty id='json-pretty' json={response}/>
            }
        </Box>
    );
};
