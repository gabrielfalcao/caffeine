import $ from 'jquery'
import _ from 'lodash'
import React from 'react'
import Dropzone from 'react-dropzone';
import HeaderView from './HeaderView.jsx'
import TrackListView from './TrackListView.jsx'
import LoadingView from './LoadingView.jsx'

import AuthenticatedView from './AuthenticatedView.jsx'

import ErrorView from './ErrorView.jsx'
import FileListView from './FileListView.jsx';

import { Col, Panel, Well, Button, Table } from 'react-bootstrap';
import {connect} from 'react-redux';

import APIClient from '../networking.jsx';


class UploadView extends React.Component {
    propTypes: {
        files: React.PropTypes.array,
        readyToDrop: React.PropTypes.bool,
        isUploading: React.PropTypes.bool,
    }
    constructor() {
        super();
        this.api = new APIClient();
        this.onDrop = this.onDrop.bind(this);
        this.onOpenClick = this.onDrop.bind(this);
        this.onDragStart = this.onDragStart.bind(this);
        this.onDragLeave = this.onDragLeave.bind(this);
        this.onUploadDone = this.onUploadDone.bind(this);
        this.doUpload = this.doUpload.bind(this);
        this.readyToDrop = false;
    }
    doUpload(e){
        const {files} = this.props;
        const {store} = this.context;
        store.dispatch({type: "UPLOAD_START"});
        let payload = JSON.stringify(files);
        this.api.uploadFiles('/api/tracks', payload, files, this.onUploadDone);
    }
    onUploadDone(){
        const {store} = this.context;
        store.dispatch({
            type: "CLEAR_FILES",
        });
    }
    onDragStart(){
        const {store} = this.context;
        this.readyToDrop = true;
        store.dispatch({
            type: "DRAG_START",
        });

    }
    onDragLeave(){
        const {store} = this.context;
        this.readyToDrop = false;
        store.dispatch({
            type: "DRAG_LEAVE",
        });
    }
    onDrop(files) {
        const {store} = this.context;
        store.dispatch({
            files: files,
            type: "ADD_FILES_FOR_UPLOAD",
        });
        console.log(files);
    }
    render() {
        const {files, readyToDrop, isUploading} = this.props;
        return (
            <AuthenticatedView>
                <HeaderView navigation={true} />

                <div className="container">
                    <Col md={12}>
                    <h1>Upload Tracks</h1>
                    <br />
                    {isUploading ? (
                        <LoadingView><h1>uploading tracks...</h1></LoadingView>) : (
                            <div>
                            <p>{(files.length > 0) ? <Button onClick={this.doUpload} bsStyle="info">send {files.length} tunes to the tank</Button> : null}</p>
                        <p>
                        <Dropzone ref="dropzone" onDrop={this.onDrop} onDragStart={this.onDragStart} onDragLeave={this.onDragLeave} className="caffeine-dropzone">
                            {(this.readyToDrop || (files.length > 0)) ? <FileListView files={files} /> : <div>
                             <h4>Drag-and-drop your music files here.</h4>
                             <Col md={6}>
                             <Well>
                             <p> Accepted formats:</p>
                             <ul>
                             <li><code>*.wav</code></li>
                             <li><code>*.mp3</code> [automatic ID3 tag extraction]</li>
                             </ul></Well></Col>
                             </div>}
                        </Dropzone></p>
                    <p>{(files.length > 0) ? <Button onClick={this.doUpload} bsStyle="info">send {files.length} tunes to the tank</Button> : null}</p>
                    </div>)}
                    </Col>
                </div>
                <br />
                <br />
                <div className="container">
                    <Col md={12}>
                    <TrackListView />
                    </Col>
                </div>

            </AuthenticatedView>
        )
    }
}

UploadView.contextTypes = {
    store: React.PropTypes.object
};

export default UploadView = connect(
    (state) => {
        return {
            files: state.files || [],
            readyToDrop: state.readyToDrop || false,
            isUploading: state.isUploading || false,
        }
    },
    (dispatch) => {
        return {
        }
    },
)(UploadView);
