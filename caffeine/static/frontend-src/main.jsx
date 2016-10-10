import  '../styles/app.less'

import React from 'react'
import {render} from 'react-dom'
import {Provider} from 'react-redux'
import {createStore, compose} from 'redux'
import {CaffeineApplication} from './reducers.jsx'

// First we import some components...
import { Router, Route } from 'react-router'
import {loadState, saveState, clearState} from './models.jsx'
import IndexView from './views/IndexView.jsx'


import history from './core.jsx'

import $ from 'jquery'

$(function(){
    let store = createStore(CaffeineApplication, loadState(), compose(
        window.devToolsExtension ? window.devToolsExtension() : f => f
    ));

    render((<Provider store={store}>
    <Router history={history}>
        <Route path="/" component={IndexView} />
    </Router>
    </Provider>), document.getElementById('app-container'))
})
