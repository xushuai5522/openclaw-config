// Use Chrome DevTools Protocol to interact with the page
const ws = require('ws');

const wsUrl = 'ws://127.0.0.1:18800/devtools/page/3A39C98639B266084A5231D0FA51F43D';

async function main() {
    const ws = new WebSocket(wsUrl);
    
    let id = 1;
    const callbacks = new Map();
    
    ws.on('open', () => {
        console.log('Connected');
        
        // Send command to evaluate JavaScript
        sendCommand('Runtime.evaluate', {
            expression: `
                // Try to find and click the CPU dropdown
                const dropdown = document.querySelector('.ant-select-selection[placeholder="请选择"]');
                if (dropdown) {
                    dropdown.click();
                    'clicked';
                } else {
                    'not found';
                }
            `
        });
    });
    
    ws.on('message', (data) => {
        const msg = JSON.parse(data);
        if (msg.id) {
            const cb = callbacks.get(msg.id);
            if (cb) cb(msg.result);
        }
        if (msg.method === 'Runtime.bindingCalled') {
            console.log('Binding called:', msg.params.name, msg.params.payload);
        }
    });
    
    function sendCommand(method, params) {
        const msg = { id: id++, method, params };
        ws.send(JSON.stringify(msg));
        return new Promise(resolve => callbacks.set(msg.id, resolve));
    }
}

main().catch(console.error);
