import $ from 'jquery'
import _ from 'lodash'
import React from 'react'
import HeaderView from './HeaderView.jsx'

import AuthenticatedView from './AuthenticatedView.jsx'
import PlayerView from './PlayerView.jsx'
import LoadingView from './LoadingView.jsx'

import ErrorView from './ErrorView.jsx'
import FileListView from './FileListView.jsx';

import { Col, Well, Button, Table, Form, FormControl, FormGroup, ControlLabel } from 'react-bootstrap';
import {connect} from 'react-redux';

import APIClient from '../networking.jsx';


class TrackEditView extends React.Component {
    propTypes: {
        track: React.PropTypes.object,
    }
    constructor() {
        super();
        this.api = new APIClient();
    }
    componentDidMount() {
        this.api.getTrack(this.props.params.track_id, this.onTrackReceived.bind(this));
    }
    editTrack(){
        const {store} = this.context;
        const data = {};
        data['title'] = $("#titleField").val();
        data['artist'] = $("#artistField").val();
        data['album'] = $("#albumField").val();
        data['genre'] = $("#genreField").val();
        store.dispatch({type: "UPLOAD_START"});
        this.api.editTrack(this.props.params.track_id, data, this.onTrackDeleted.bind(this));
    }
    editArtwork(){
        const {store} = this.context;
        store.dispatch({type: "UPLOAD_START"});
        const files = document.getElementById("imageField").files;
        if (files.length > 0) {
            this.api.uploadArtwork(this.props.params.track_id, files, this.onTrackReceived.bind(this));
        }
    }
    deleteTrack(){
        const {store} = this.context;
        store.dispatch({type: "UPLOAD_START"});
        this.api.deleteTrack(this.props.params.track_id, this.onTrackDeleted.bind(this));
    }
    reprocessTrack(){
        const {store} = this.context;
        store.dispatch({type: "UPLOAD_START"});
        this.api.reprocessTrack(this.props.params.track_id, this.onTrackReceived.bind(this));
    }
    onTrackReceived(result, err){
        const {store} = this.context;

        if (!err){
            store.dispatch({
                track: result,
                type: "SET_CURRENT_TRACK",
            });
        } else {
            store.dispatch({type: "UPLOAD_END"});
        }
    }
    onTrackDeleted(result, err){
        location.href = '/'
    }
    render() {
        const {track, isUploading} = this.props;
        return (
            <AuthenticatedView>
                <HeaderView navigation={true} />

                <div className="container">
                    <Col md={12}>
                    {isUploading ? (
                        <LoadingView><h1>saving...</h1></LoadingView>) : (
                            <Well>
                        <Form horizontal>
                        <FormGroup>
                            <Col className="text-right" componentClass={ControlLabel} sm={2}><h2>{track.title} by {track.artist}</h2></Col>
                          <Col sm={10}>
                          <img src={track.artwork_url} width={400} height={400} className="img-square img-responsive"/>
                          <input type="file" name="artwork" accept="image/*" id="imageField" onChange={this.editArtwork.bind(this)}/>
                          </Col>
                        </FormGroup>
                        <FormGroup>
                          <Col componentClass={ControlLabel} sm={2}></Col>
                          <Col sm={10}>
                            <PlayerView track={track} />
                          </Col>
                        </FormGroup>
                        <FormGroup>
                          <Col componentClass={ControlLabel} sm={2}>Title</Col>
                          <Col sm={10}>
                            <FormControl type="input" placeholder={track.title}  id="titleField" />
                          </Col>
                        </FormGroup>
                        <FormGroup>
                          <Col componentClass={ControlLabel} sm={2}>Artist</Col>
                          <Col sm={10}>
                            <FormControl type="input" placeholder={track.artist} id="artistField" />
                          </Col>
                        </FormGroup>
                        <FormGroup>
                          <Col componentClass={ControlLabel} sm={2}>Album</Col>
                          <Col sm={10}>
                            <FormControl type="input" placeholder={track.album}  id="albumField" />
                          </Col>
                        </FormGroup>
                        <FormGroup>
                          <Col componentClass={ControlLabel} sm={2}>Genre</Col>
                          <Col sm={10}>
                            <FormControl type="input" placeholder={track.genre}  id="genreField" />
                          </Col>
                        </FormGroup>
                        <FormGroup>
                            <Col smOffset={2} sm={10}>
                          <Button className="col-sm-12 col-md-2" bsStyle="primary" onClick={this.editTrack.bind(this)}>save</Button>
                          <a className="btn btn-success" href={track.download_url}>download</a>
                          <Button className="col-sm-12 col-md-2" bsStyle="warning" onClick={this.reprocessTrack.bind(this)}>re-process track</Button>
                          <Button className="col-sm-12 col-md-2" bsStyle="danger" onClick={this.deleteTrack.bind(this)}>delete track</Button>
                          </Col>
                        </FormGroup>
                      </Form>
                    </Well>)}
                </Col>
                </div>
            </AuthenticatedView>
        )
    }
}

TrackEditView.contextTypes = {
    store: React.PropTypes.object
};

export default TrackEditView = connect(
    (state) => {
        return {
            track: state.track || {},
            isUploading: state.isUploading || false,
        }
    },
    (dispatch) => {
        return {
        }
    },
)(TrackEditView);
