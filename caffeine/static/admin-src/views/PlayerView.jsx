import $ from 'jquery'
import _ from 'lodash'
import React from 'react'

import Wavesurfer from 'react-wavesurfer';
import { Col, Panel, Button, Table } from 'react-bootstrap';
import {connect} from 'react-redux';

import APIClient from '../networking.jsx';

function zero_pad(num) {
    const pad = "00";
    const str = parseInt(num) + "";
    return pad.substring(0, pad.length - str.length) + str;
}

class PlayerView extends React.Component {
    propTypes: {
        track: React.PropTypes.object,
    }
    constructor() {
        super();
        this.state = {
            playing: false,
            pos: 0,
            volume: 1.0
        };
    }
    handleFinish(e) {
        this.setState({
            pos: 0,
            playing: false
        });
    }
    handlePosChange(e) {
        this.setState({
            pos: e.originalArgs ? e.originalArgs[0] : +e.target.value
        });
    }
    handleVolumeChange(e) {
        this.setState({
            volume: +e.target.value
        });
    }

    handleReady() {
        this.setState({
            pos: 0
        });
    }
    handleTogglePlay() {
        this.setState({
            playing: !this.state.playing
        });
    }
    render() {
        const {track} = this.props;
        const waveOptions = {
            fillParent: true,
            scrollParent: false,
            height: 100,
            progressColor: '#B25FAC',
            waveColor: '#2899b2',
            cursorColor: '#fff',
            cursorWidth: 3,
            barWidth: 3,
        };
        return (
            <div>
                <Col md={12} sm={12}>
                <Wavesurfer
                  volume={this.state.volume}
                  pos={this.state.pos}
                  options={waveOptions}
                  onFinish={this.handleFinish.bind(this)}
                  onPosChange={this.handlePosChange.bind(this)}
                  audioFile={track.download_url}
                  playing={this.state.playing}
                  onReady={this.handleReady.bind(this)}
                /></Col>
                <br />
                <Col md={1}><Button className={"ion-" + (this.state.playing ? "pause" : "play")} bsStyle="primary" bsSize="small" onClick={this.handleTogglePlay.bind(this)} style={{fontSize: "24px"}}></Button></Col>
                <Col md={1}><div style={{fontSize: "24px", padding: 0, margin: 0}}>{[zero_pad(this.state.pos / 360), zero_pad((this.state.pos / 60) % 60), zero_pad(this.state.pos % 60)].join(":")}</div></Col>
            </div>
        )
    }
}

PlayerView.contextTypes = {
    store: React.PropTypes.object
};

export default PlayerView = connect(
    (state) => {
        return {
            track: state.track || {},
        }
    },
    (dispatch) => {
        return {
        }
    },
)(PlayerView);
