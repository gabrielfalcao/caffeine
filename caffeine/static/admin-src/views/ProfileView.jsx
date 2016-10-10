import $ from 'jquery'
import _ from 'lodash'
import React from 'react'
import HeaderView from './HeaderView.jsx'

import AuthenticatedView from './AuthenticatedView.jsx'

import { Col, Panel, Button, Table } from 'react-bootstrap';
import {connect} from 'react-redux';

import APIClient from '../networking.jsx';


class ProfileView extends React.Component {
    propTypes: {
        user: React.PropTypes.object,
    }
    constructor() {
        super();
    }
    render() {
        const {user} = this.props;
        return (
            <AuthenticatedView>
                <HeaderView navigation={true} />
                <div className="container">
                    <Col md={6}>
                        <p><strong>Name:</strong>&nbsp; {user.name}</p>
                        <p><strong>Email:</strong>&nbsp; {user.email}</p>
                        <p><a href="/logout">Logout</a></p>
                    </Col>
                    <Col md={6}>
                        <p><img src={user.avatar} /></p>
                    </Col>
                </div>
            </AuthenticatedView>
        )
    }
}

ProfileView.contextTypes = {
    store: React.PropTypes.object
};

export default ProfileView = connect(
    (state) => {
        return {
            user: state.user || {},
        }
    },
    (dispatch) => {
        return {
        }
    },
)(ProfileView);
