import $ from 'jquery'
import _ from 'lodash'
import React from 'react'
import HeaderView from './HeaderView.jsx'

import AuthenticatedView from './AuthenticatedView.jsx'
import TrackListView from './TrackListView.jsx'

import ErrorView from './ErrorView.jsx'

import { Col, Panel, Button } from 'react-bootstrap';
import {connect} from 'react-redux';

import APIClient from '../networking.jsx';


class IndexView extends React.Component {
    propTypes: {
        projects: React.PropTypes.array,
        repos: React.PropTypes.array,
        errors: React.PropTypes.array,
    }
    constructor() {
        super();
        this.api = new APIClient();
    }
    render() {
        const {projects, repos, errors} = this.props;
        return (
            <AuthenticatedView>
                <HeaderView navigation={true} />
                <TrackListView />
            </AuthenticatedView>
        )
    }
}

IndexView.contextTypes = {
    store: React.PropTypes.object
};

export default IndexView = connect(
    (state) => {
        return {
            projects: state.projects || [],
            repos: state.repos || [],
            errors: state.errors || [],
        }
    },
    (dispatch) => {
        return {
        }
    },
)(IndexView);
