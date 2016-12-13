export class Message {
    constructor(name, data) {
        this.name = name;
        this.data = data;
    }

    static fromString(string) {
        if ('string' !== typeof string) {
            const msg = 'SockMessage.fromString must get a string as argument';

            if (console.warn) {
                console.warn(msg);
            } else {
                throw new Error(msg);
            }
        }

        const values = string.split('|');
        const name = values[0];
        const data = JSON.parse(values[1]);

        return new Message(name, data);
    }

    toString() {
        return this.name + '|' + JSON.stringify(this.data);
    }
}


export class Socker {
    constructor(uri, reconnect) {
        // Reconnect automatically
        this.reconnect = (typeof reconnect == 'undefined') ? true : reconnect;

        // Print logging
        this.debug = true;

        this.wsURI = uri;

        this.listeners = {};
        this.queue = [];

        this._reconnectTimeoutID = null;
        this.reconnectTimeout = 15000;

        this.bundleSubscriptions = true;
        this.bundleTimeout = 1;
        this._bundleTimeoutID = null;

        this._connect();
    }

    isConnected() {
        return this.ws.readyState == WebSocket.OPEN;
    }

    send(message) {
        if (!this.isConnected()) {
            this.log('Not connected. Putting message in queue.');
            this.queue.push(message);
            return;
        }

        this._send(message.toString());
    }

    on(name, cb) {
        if (!this.listeners.hasOwnProperty(name)) {
            this.listeners[name] = [];
            this._subscribeAll();
        }

        this.listeners[name].push(cb);
    }

    off(name, func) {
        const self = this;

        if (!this.listeners.hasOwnProperty(name)) {
            self.log('Could not off event handlers, no subscribers to', name);
        }

        this.listeners[name].forEach((callback, i) => {
            if (callback == func) {
                this.listeners[name].splice(i);
            }
        });

        // Remove channel key if empty
        if (!self.listeners[name].length) {
            delete this.listeners[name];
        }
    }

    emit(name, data) {
        this.send(new Message(name, data).toString());
    }

    _connect(_reconnecting) {
        this.log('socker connecting to', this.wsURI);

        this.ws = new WebSocket(this.wsURI);

        this.ws.addEventListener('open', function(e) {
            if (this._reconnectTimeoutID) {
                clearTimeout(this._reconnectTimeoutID);
            }
            this._reconnectTimeoutID = null;

            this.log('Connected');

            if (_reconnecting) {
                this._subscribeAll();
            }

            this._sendAll();
        }.bind(this));

        this.ws.addEventListener('message', this._onMessage.bind(this));

        this.ws.addEventListener('close', this._onClose.bind(this));
    }

    _onMessage(e) {
        this.log('sock << ' + e.data);
        if (e.data.indexOf('#') == 0) {  // Message starts with '#'
            return
        }
        const message = Message.fromString(e.data);
        const handlers = this.listeners[message.name] || [];

        handlers.forEach(function (handler) {
            handler(message.data, message, e);
        });
    }

    _onClose(e) {
        this.log('Connection closed');
        this._closed = true;

        if (this.reconnect) {
            this.log('Reconnecting in ' + this.reconnectTimeout / 1000
                      + ' seconds.');

            this._reconnectTimeoutID = setTimeout(
                this._reconnect.bind(this), this.reconnectTimeout);
        }
    }

    _reconnect() {
        this.log('reconnecting...');
        this._connect(true);  // Indicate to _connect that we are reconnecting.
    }

    _sendAll() {
        this.queue.forEach(function (message) {
            this._send(message.toString());
        }.bind(this));
    }

    _send(string) {
        this.log('sock >> ' + string);

        this.ws.send(string)
    }

    _subscribeAll() {
        const channels = Object.keys(this.listeners);

        if (this.bundleSubscriptions) {
            if (this._bundleTimeoutID) {
                clearTimeout(this._bundleTimeoutID);
            }
            this.log('Bundling subscriptions');

            this._bundleTimeoutID = setTimeout(() => {
                this._subscribe(channels);
            }, this.bundleTimeout);

            return;
        }

        this._subscribe(channels);
    }

    _subscribe(channels) {
        this.emit('set-subscriptions', channels);
    }

    log(...args) {
        if (this.debug) {
            console.log.apply(console, args);
        }
    }

    toString() {
        let status = 'UNKNOWN';
        const stateMap = {
          0: 'CONNECTING',
          1: 'OPEN',
          2: 'CLOSING',
          3: 'CLOSED'
        };

        if (this.ws) {
            status = stateMap[this.ws.readyState];
        }

        return '<Socker uri=' + this.wsURI + ' status=' + status + '>';
    }
}
