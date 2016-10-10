import $ from 'jquery'
import _ from 'lodash'
import React from 'react'
import Dropzone from 'react-dropzone';
import HeaderView from './HeaderView.jsx'

import AuthenticatedView from './AuthenticatedView.jsx'

import ErrorView from './ErrorView.jsx'

import { Col, Panel, Button, Table } from 'react-bootstrap';
import {connect} from 'react-redux';

import APIClient from '../networking.jsx';

class FileListView extends React.Component {
    propTypes: {
        files: React.PropTypes.array,
    }
    render() {
        let totalBytes = 0;
        return (
            <div>
                <Table striped bordered condensed hover>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Type</th>
                        <th>Size</th>
                    </tr>
                </thead>
                <tbody>
                    {this.props.files.length == 0 ? <tr><td colspan="2">DROP!</td></tr>: null}
                    {_.map(this.props.files, (file, i) => {
                        totalBytes += file.size;
                        return <tr key={i}>
                            <td>{file.name}</td>
                            <td>{file.type}</td>
                            <td>{parseInt(file.size / 1024)} kb</td>
                        </tr>}
                     )}
                </tbody>
                </Table>
                <strong>Total upload: {parseInt(totalBytes / 1024 / 1024)} mb</strong>
            </div>
        )
    }
}


FileListView.contextTypes = {
    store: React.PropTypes.object
};

export default FileListView = connect(
    (state) => {
        return {
            files: state.files || [],
        }
    },
    (dispatch) => {
        return {
        }
    },
)(FileListView);
