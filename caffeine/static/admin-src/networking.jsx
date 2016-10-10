import request from 'superagent';
import cookie from 'react-cookie';


function handle(callback) {
    return function (err, response){
        if (err) {
            console.log("API ERROR:", err, response);
        }
        if (response) {
            console.log("API RESPONSE", response);
        }
        if (response && response.body){
            callback(response.body, err);
        }
    }
}

function getToken() {
    return cookie.load('caffeine_token');
}

class APIClient {
    constructor() {
    }
    doGET(path, callback){
        return request.get(path)
                      .set('Authorization', "Bearer: " + getToken())
                      .set('Accept', 'application/json')
                      .end(handle(callback));

    }
    doPOST(path, payload, callback) {
        return request.post(path)
                      .set('Authorization', "Bearer: " + getToken())
                      .set('Accept', 'application/json')
                      .send(payload)
                      .end(handle(callback));
    }
    doPATCH(path, payload, callback) {
        return request.patch(path)
                      .set('Authorization', "Bearer: " + getToken())
                      .set('Accept', 'application/json')
                      .send(payload)
                      .end(handle(callback));
    }
    doPUT(path, payload, callback) {
        return request.put(path)
                      .set('Authorization', "Bearer: " + getToken())
                      .set('Accept', 'application/json')
                      .send(payload)
                      .end(handle(callback));
    }
    doDELETE(path, callback) {
        return request.delete(path)
                      .set('Authorization', "Bearer: " + getToken())
                      .set('Accept', 'application/json')
                      .send()
                      .end(handle(callback));
    }
    uploadFiles(path, payload, files, callback) {
        let req = request.post(path)
                      .set('Authorization', "Bearer: " + getToken())
                      .set('Accept', 'application/json');

        for (var x in files) {
            var file = files[x];
            req.attach(file.name, file);
        }

        return req.end(handle(callback));
    }
    uploadArtwork(track_id, files, callback) {
        let req = request.put('/api/artwork/' + track_id)
                      .set('Authorization', "Bearer: " + getToken())
                      .set('Accept', 'application/json');

        for (var x in files) {
            var file = files[x];
            req.attach('artwork', file);
            // only take the first file
            break;
        }
        return req.end(handle(callback));
    }
    authenticate(callback) {
        return this.doGET('/api/user', (response, err) => {
            if (err !== null && parseInt(err.status) == 401) {

            } else {
                return callback(response, err);
            }
        });
    }
    getTrack(track_id, callback) {
        return this.doGET('/api/track/' + track_id, callback);
    }
    reprocessTrack(track_id, callback) {
        return this.doPUT('/api/track/' + track_id, {}, callback);
    }
    deleteTrack(track_id, callback) {
        return this.doDELETE('/api/track/' + track_id, callback);
    }
    editTrack(track_id, data, callback) {
        return this.doPATCH('/api/track/' + track_id, data, callback);
    }

}

export default APIClient
