import React from 'react'
import HeaderView from './HeaderView.jsx'
import { Panel, Col } from 'react-bootstrap';
var GoogleLoginButton = require("./google-login.png");

class AnonymousView extends React.Component {
    render() {
        return <div>
            <HeaderView authenticated={false} />
            <div className="container">
                <Col md={3}></Col>
                <Col md={6}>
                <Panel header={"Admin Access"} bsStyle="primary">

                    <p>Access here is restricted to selected people but is federated by Google.</p>
                    <p>Just check click below and as long as your email is known to us, you get in.</p>
                    <br />
                    <center>
                    <p><a className="ion-social-google btn btn-large btn-primary" style={{fontSize: "32px", padding: "2px 8px", margin:0}} href="/admin">&nbsp; login</a></p>
                    </center>
                </Panel>
                </Col>
                <Col md={3}></Col>
            </div>
        </div>
    }
}

export default AnonymousView
