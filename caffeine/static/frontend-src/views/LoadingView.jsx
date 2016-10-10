import React from 'react'

class LoadingView extends React.Component {
    render() {
        var self = this;
        return (
            <center>
                {this.props.children}
                <div className='uil-ball-css'><div></div></div>
                <br />
            </center>
        )
    }
}

export default LoadingView
