/* eslint-disable */
import React from 'react';
import {
    Box,
    Button,
    Heading,
    Paragraph,
    Text,
    TextArea,
} from 'grommet';


export default class Debug extends React.Component {

  render(){
    return(
      <Box
          margin={{
              horizontal: 'medium'
          }}
          pad='medium'
      >
          <Heading level='2'>
              Debug
          </Heading>
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
          </Box>
      </Box>
    )
  }
}
