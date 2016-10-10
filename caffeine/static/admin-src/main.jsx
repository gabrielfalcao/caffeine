import  '../styles/app.less'

import React from 'react'
import {render} from 'react-dom'
import {Provider} from 'react-redux'
import {createStore, compose} from 'redux'
import {CaffeineApplication} from './reducers.jsx'

// First we import some components...
import { Router, Route } from 'react-router'
import {loadState, saveState, clearState} from './models.jsx'
import HeaderView from './views/HeaderView.jsx'
import IndexView from './views/IndexView.jsx'
import UploadView from './views/UploadView.jsx'
import ProfileView from './views/ProfileView.jsx'
import TrackEditView from './views/TrackEditView.jsx'

import history from './core.jsx'

import $ from 'jquery'

$(function(){
    let store = createStore(CaffeineApplication, loadState(), compose(
        window.devToolsExtension ? window.devToolsExtension() : f => f
    ));

    render((<Provider store={store}>
    <Router history={history}>
        <Route path="/" component={IndexView} />
        <Route path="/upload" component={UploadView} />
        <Route path="/profile" component={ProfileView} />
        <Route path="/track/:track_id" component={TrackEditView} />
    </Router>
    </Provider>), document.getElementById('app-container'))
})
