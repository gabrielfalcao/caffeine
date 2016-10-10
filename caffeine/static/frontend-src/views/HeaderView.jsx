import React from 'react'
import { Navbar, Nav, NavDropdown, NavItem, MenuItem, Col } from 'react-bootstrap';
import {connect} from 'react-redux';

import APIClient from '../networking.jsx';

class HeaderView extends React.Component {
    propTypes: {
        user: React.PropTypes.object,
    }
    constructor() {
        super();
        this.api = new APIClient();
    }
    componentWillMount(){
    }
    render() {
        const {user} = this.props;
        return (
            <Navbar>
                <Navbar.Header>
                    <Navbar.Brand>
                        <a href="/">CAFFEINE</a>
                    </Navbar.Brand>
                    <Navbar.Toggle />
                </Navbar.Header>
            </Navbar>
        )
    }
}


HeaderView.contextTypes = {
    store: React.PropTypes.object
};

export default HeaderView = connect(
    (state) => {
        return {
            user: state.user || {},
        }
    },
    (dispatch) => {
        return {
        }
    },
)(HeaderView);
