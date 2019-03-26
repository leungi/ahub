import React from 'react';
import {
    Grommet,
    Grid,
    Box,
    Image,
} from 'grommet'
import {
    Router,
} from '@reach/router';
import { get } from '../modules/fetch';
import MainNavLink from './MainNavLink';
import NodeBox from './NodeBox';
import Debug from './Debug';
import AhubLogo from '../assets/ahub_logo.png';


//const API_ENDPOINT = 'http://ahub.westeurope.cloudapp.azure.com:8000/';
const API_ENDPOINT = window.location.href

const theme = {
    global: {
        colors: {
            brand: '#f8f8f8',
            'accent-1': '#009fe3',
            'neutral-1': '#aaa',
        },
        font: {
            family: 'Roboto',
            size: '14px',
            height: '20px',
        },
    },
};

export default class AhubGUI extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            nodes: []
        };
    }

    componentDidMount() {
        get(`${API_ENDPOINT}boss/get_services`)
            .then(response => this.setState({ nodes: response.apis }))
            .catch(err => {
                console.warn(err);
                // prefill nodes for testing purposes
                this.setState({ nodes: ['node1', 'node2'] });
            });
    }

    render() {
        return (
            <Grommet
                theme={theme}
                full
            >
                    <Grid
                        fill
                        areas={[
                            { name: 'nav', start: [0, 0], end: [0, 0] },
                            { name: 'main', start: [1, 0], end: [1, 0] }
                        ]}
                        columns={['small', 'flex']}
                        rows={['flex']}
                        gap='none'
                    >
                        <Box
                            gridArea='nav'
                            background='brand'
                            pad='medium'
                        >
                            <Box>
                                <Image className='logo'
                                    src={AhubLogo}
                                />
                            </Box>
                            <Box
                                tag='nav'
                                direction='column'
                                margin={{
                                    vertical: 'large'
                                }}
                            >
                                <MainNavLink to='/'>Home</MainNavLink>
                                {
                                    this.state.nodes
                                    && this.state.nodes.map(node => (
                                        <MainNavLink
                                            key={`navlink-${node}`}
                                            to={node}
                                        >
                                            {node}
                                        </MainNavLink>
                                    ))
                                }
                                <MainNavLink to='debug'>Debug</MainNavLink>
                            </Box>
                        </Box>
                        <Box
                            gridArea='main'
                            background='brand'
                        >
                            <Router>
                                {
                                    this.state.nodes
                                    && this.state.nodes.map(node => (
                                        <NodeBox
                                            key={`nodebox-${node}`}
                                            path={node}
                                            name={node}
                                        />
                                    ))
                                }
                                <Debug path='/debug'/>
                            </Router>
                        </Box>
                    </Grid>
            </Grommet>
        )
    }
}
