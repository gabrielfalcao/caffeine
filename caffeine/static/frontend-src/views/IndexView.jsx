import $ from 'jquery'
import _ from 'lodash'
import React from 'react'
import HeaderView from './HeaderView.jsx'
import ErrorView from './ErrorView.jsx'

import { Col, Panel, Button } from 'react-bootstrap';
import {connect} from 'react-redux';

class IndexView extends React.Component {
    propTypes: {
        projects: React.PropTypes.array,
        repos: React.PropTypes.array,
        errors: React.PropTypes.array,
    }
    constructor() {
        super();
    }
    render() {
        const {projects, repos, errors} = this.props;
        return (
            <div>
            <HeaderView navigation={true} />
            <div className="container">
                <h1>Caffeine</h1>
            </div>
            </div>
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
