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

class TrackListView extends React.Component {
    propTypes: {
        tracks: React.PropTypes.array,
    }
    constructor() {
        super();
        this.api = new APIClient();
        this.onReceiveTracks = this.onReceiveTracks.bind(this);
        this.refresh = this.refresh.bind(this);
    }
    refresh(){
        this.api.doGET('/api/tracks', this.onReceiveTracks);
    }
    componentDidMount() {
        this.refresh();
        this.timer = setInterval(() => {
            this.refresh();
        }.bind(this), 5000);
    }
    componentWillUnmount() {
        clearInterval(this.timer);
    }
    deleteTrack(track_id){
        this.api.deleteTrack(track_id, this.onTrackDeleted.bind(this));
    }
    onTrackDeleted(){
        this.refresh()
    }
    onReceiveTracks(result, err){
        const {store} = this.context;
        if (!err){
            store.dispatch({
                tracks: result.tracks,
                type: "LIST_TRACKS",
            });
        }
    }
    render() {
        let totalBytes = 0;
        const {tracks} = this.props;
        return (
            <div className="container">
                <h1>{tracks.length} Tracks in the cloud</h1>
                <Table striped bordered condensed hover responsive>
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Artist</th>
                        <th>Artwork</th>
                        <th>Uploader</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {_.map(tracks, (track, i) => {
                        totalBytes += track.size;
                        return <tr key={i}>
                        <td><a className="text-warning" href={"/#/track/" + track.id}>{track.title}</a></td>
                        <td>{track.artist}</td>
                        <td><center><img src={track.artwork_url} width={48} height={48} style={{margin: 0, padding: 0}} className="img-circle" /></center></td>
                        <td>{track.user.name}</td>
                        <td><center>
                        &nbsp;<a style={{fontSize: "32px"}} className="text-success ion-ios-cloud-download" href={track.download_url}></a>&nbsp;
                        &nbsp;<a style={{fontSize: "32px"}} className="text-warning ion-edit" href={"/#/track/" + track.id}></a>&nbsp;
                        &nbsp;<a style={{fontSize: "32px"}} className="text-danger ion-backspace" onClick={() => { this.deleteTrack(track.id)}}></a>&nbsp;
                        </center>
                        </td>
                        </tr>}
                     )}
                </tbody>
                </Table>
            </div>
        )
    }
}


TrackListView.contextTypes = {
    store: React.PropTypes.object
};

export default TrackListView = connect(
    (state) => {
        return {
            tracks: state.tracks || [],
        }
    },
    (dispatch) => {
        return {
        }
    },
)(TrackListView);
