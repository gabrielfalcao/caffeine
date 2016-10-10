import React from 'react'
import { Navbar, Nav, NavDropdown, NavItem, MenuItem, Col } from 'react-bootstrap';
import {connect} from 'react-redux';

import APIClient from '../networking.jsx';

var Logo = require("./navbar-logo.png");


class HeaderView extends React.Component {
    propTypes: {
        user: React.PropTypes.object,
    }
    constructor() {
        super();
        this.api = new APIClient();
        this.refresh = this.refresh.bind(this);
    }
    refresh(){
        const {store} = this.context;
        this.api.authenticate((result, err) => {
            if (!err) {
                store.dispatch({
                    user: result,
                    type: "SET_USER",
                })
            }
        });
    }
    componentWillMount(){
        this.refresh();
    }
    render() {
        const {user} = this.props;
        return (
            <Navbar>
                <Navbar.Header>
                    <Navbar.Brand>
                        <a href="/"><img src={Logo}/></a>
                    </Navbar.Brand>
                    <Navbar.Toggle />
                </Navbar.Header>
                {this.props.navigation ? <Navbar.Collapse>
                 <Nav pullRight>
                 <NavItem href="#/upload">Upload Tracks</NavItem>
                 <NavDropdown title={user.name} id="basic-nav-dropdown">
                 <MenuItem href="#/profile">Profile</MenuItem>
                 <MenuItem href="/logout">Logout</MenuItem>
                 </NavDropdown>
                 </Nav>

                 </Navbar.Collapse> : null}
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
