import {_} from 'lodash';
import cookie from 'react-cookie';

export const CaffeineApplication = (state, action) => {
    const user_token = cookie.load('caffeine_token');
    switch (action.type) {
        case "CLEAR_FILES":
            return {...state, files: [], isUploading: false}
            break;

        case "LIST_TRACKS":
            return {...state, tracks: action.tracks}
            break;
        case "SET_CURRENT_TRACK":
            return {...state, track: action.track, isUploading: false}
            break;
        case "ADD_FILES_FOR_UPLOAD":
            let files1 = [...state.files || []];
            files1 = [...files1, ...action.files];
            let names1 = [];
            let filtered1 = [];
            for (let x in files1) {
                let y = files1[x];
                if ((names1.indexOf(y.name) < 0) && y.type.match(/^audio.(mp3|wav)/)){
                    filtered1.push(y);
                }
                names1.push(y.name);
            }
            return {...state, files: filtered1}
            break;
        case "UNSET_FILE_FOR_UPLOAD":
            let files2 = [...state.files || []];
            let filtered2 = [];
            for (let x in files2) {
                let y = files2[x];
                if (y.name !== action.file.name) {
                    filtered2.push(y);
                }
            }
            return {...state, files: filtered2};
            break;
        case "DRAG_START":
            return {...state, readyToDrop: true}
            break;
        case "DRAG_LEAVE":
            return {...state, readyToDrop: false}
            break;
        case "UPLOAD_START":
            return {...state, isUploading: true}
            break;
        case "UPLOAD_END":
            return {...state, isUploading: false}
            break;
        case "SET_USER":
            return {...state, user: action.user}
            break;
        case "CLEAR_ERRORS":
            return {...state, errors: []}
            break;
        case "ERROR":
            let errors = [...state.errors || [], {"message": action.message}];
            console.log(errors)
            return {...state, errors: errors}
            break;
        default:
            return {...state, user_token: user_token};
            break;
    }
}
