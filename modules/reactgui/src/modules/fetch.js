/**
 * Wrapper for server calls
 *
 * Uses native browser method fetch or polyfill if not implemented
 * Per default calls can only be made to the same host and only have a JSON body.
 */
import 'whatwg-fetch';
import JSONPretty from 'react-json-pretty';

const POST = 'POST';
const GET = 'GET';
const JSON_CONTENT = 'application/json';

/**
 * @param {String} method           - GET | POST
 * @param {String} url              - the resource to call
 * @param {Object} data             - payload of a (post) call, has to be valid JSON
 * @param {Object} requestOptions   - (optional) fetch request options
 * @see https://developer.mozilla.org/en-US/docs/Web/API/WindowOrWorkerGlobalScope/fetch#Parameters
 * @returns {Promise}
 */
function fetchData(method, url, data, requestOptions = {}) {
    let isSuccess = false;
    const methodName = method.toUpperCase();

    const requestBody = {
        method: methodName,
        headers: {
            //'Content-Type': JSON_CONTENT,
            Accept: JSON_CONTENT,
        },
        // credentials: 'same-origin',
        ...requestOptions,
    };

    if (method === POST) {
        requestBody.body = JSON.stringify(data);
    }

    return global.fetch(url, requestBody)
        .then(response => {
            if (response.ok) {
                isSuccess = true;
            }

            return response.json();
        })
        .then(responseBody => {
            if (isSuccess) {
                return responseBody;
            }

            throw new Error(responseBody.message);
        })
        .catch(err => {
            throw err;
        });
}


export function get(url) {
    return fetchData(GET, url);
}

export function post(url, data) {
    return fetchData(POST, url, data);
}
