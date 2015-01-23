# socker.js - socker client

socker.js is the client for https://github.com/5monkeys/socker.


## Example

    var socker = new Socker('ws://sock.example:8765');
      
    socker.on('hello', function (data) {
        console.log('From server:', data);
    });
    socker.emit('hello', {foo: 'bar'});


