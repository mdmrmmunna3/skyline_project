// Copyright 2021 99cloud
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import Axios from 'axios';
import { isEmpty } from 'lodash';
import qs from 'qs';
import { v4 as uuidv4 } from 'uuid';

const METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'COPY'];

/**
 * @class HttpRequest
 * Axios wrapper for Skyline (cookie-based auth)
 */
export class HttpRequest {
  constructor() {
    this.request = {};
  }

  goToLoginPage(path) {
    const globalRootStore = require('stores/root').default;
    globalRootStore.goToLoginPage(path);
  }

  handleError(error) {
    const { response } = error;
    if (response && response.status === 401) {
      const currentPath = window.location.pathname;
      if (!currentPath.includes('login')) {
        this.goToLoginPage(currentPath);
      }
    }
  }

  addRequestId(config) {
    const uuid = uuidv4();
    config.headers['X-Openstack-Request-Id'] = `req-${uuid}`;
  }

  // ❌ Token-based auth REMOVED (Skyline uses cookie session)

  addVersion(config, url) {
    const { getOpenstackApiVersion } = require('./constants');
    const apiVersionMap = getOpenstackApiVersion(url);
    if (apiVersionMap) {
      config.headers[apiVersionMap.key] = apiVersionMap.value;
    }
  }

  updateHeaderByConfig(config) {
    const { options: { headers, isFormData, ...rest } = {} } = config;

    if (!isEmpty(headers)) {
      config.headers = {
        ...config.headers,
        ...headers,
      };
    }

    if (isFormData) {
      delete config.headers['Content-Type'];
    }

    Object.keys(rest).forEach((key) => {
      config[key] = rest[key];
    });
  }

  updateRequestConfig(config, url) {
    this.addRequestId(config);
    this.addVersion(config, url);
    this.updateHeaderByConfig(config);
    return config;
  }

  handleResponse(response) {
    return response;
  }

  interceptors(instance, url) {
    instance.interceptors.request.use(
      (config) => this.updateRequestConfig(config, url),
      (err) => Promise.reject(err)
    );

    instance.interceptors.response.use(
      (response) => {
        this.handleResponse(response);
        const { data, status } = response;
        if (status < 200 || status >= 300) {
          return Promise.reject(data);
        }
        return data;
      },
      (error) => {
        console.log('Axios error:', error);
        if (error.response) {
          this.handleError(error);
          return Promise.reject(error.response.data);
        }
        return Promise.reject(new Error('Network / CORS error'));
      }
    );
  }

  /**
   * Create axios instance (COOKIE-BASED AUTH)
   */
  create() {
    const conf = {
      baseURL: 'http://127.0.0.1:28000/',
      withCredentials: true, // ✅ REQUIRED for skyline_session cookie
      headers: {
        'Content-Type': 'application/json;charset=utf-8',
        'cache-control': 'no-cache',
        pragma: 'no-cache',
      },
    };
    return Axios.create(conf);
  }

  omitNil(obj) {
    if (typeof obj !== 'object') return obj;
    return Object.keys(obj).reduce((acc, v) => {
      if (obj[v] !== undefined && obj[v] !== null && obj[v] !== '') acc[v] = obj[v];
      return acc;
    }, {});
  }

  trimParams(value) {
    if (value == null) return value;
    if (typeof value === 'string') return value.trim();
    if (Array.isArray(value)) return value.map((item) => this.trimParams(item));
    if (typeof value === 'object') {
      return Object.keys(value).reduce((acc, key) => {
        acc[key] = this.trimParams(value[key]);
        return acc;
      }, {});
    }
    return value;
  }

  buildRequest(config) {
    const method = config.method ? config.method.toLowerCase() : 'get';
    const options = { ...config };

    if (options.params && ['get', 'head'].includes(method)) {
      options.params = this.trimParams(this.omitNil(options.params));
      options.paramsSerializer = (p) => qs.stringify(p, { arrayFormat: 'repeat' });
    }

    const instance = this.create();
    this.interceptors(instance, options.url);
    return instance(options);
  }

  generateRequestMap = () => {
    METHODS.forEach((method) => {
      const lowerMethod = method.toLowerCase();
      if (['get', 'head', 'copy'].includes(lowerMethod)) {
        this.request['get'] = (url, params = {}, options) =>
          this.buildRequest({ method: 'get', url, params, options });
      } else {
        this.request['post'] = (url, data, params, options) =>
          this.buildRequest({ method: 'post', url, data, params, options });
      }
    });

    this.request.empty = () => ({});
  };
}

const httpRequest = new HttpRequest();
httpRequest.generateRequestMap();
export default httpRequest;
