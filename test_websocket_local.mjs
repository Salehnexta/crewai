#!/usr/bin/env node
import WebSocket from 'ws';

const testWebSocket = async () => {
    console.log('🧪 Testing Local WebSocket Connection');
    console.log('==========================================');
    
    const wsUrl = 'ws://localhost:8090/ws/test_user';
    console.log(`📡 Connecting to: ${wsUrl}`);
    
    try {
        const ws = new WebSocket(wsUrl);
        
        ws.on('open', () => {
            console.log('✅ WebSocket connection established!');
            
            // Send a test message
            setTimeout(() => {
                const testMessage = {
                    content: 'مرحبا',
                    user_id: 'test_user',
                    session_id: 'test_session'
                };
                console.log('📤 Sending test message:', testMessage);
                ws.send(JSON.stringify(testMessage));
            }, 1000);
        });
        
        ws.on('message', (data) => {
            try {
                const message = JSON.parse(data.toString());
                console.log('📥 Received message:', message);
                
                // Send another test message
                if (message.type === 'welcome') {
                    setTimeout(() => {
                        const testMessage2 = {
                            content: 'أريد تحليل موقعي',
                            user_id: 'test_user',
                            session_id: 'test_session'
                        };
                        console.log('📤 Sending second test message:', testMessage2);
                        ws.send(JSON.stringify(testMessage2));
                    }, 2000);
                }
                
                // Close after testing
                if (message.type === 'message' && message.intent_detected) {
                    setTimeout(() => {
                        console.log('✅ All tests passed! Closing connection...');
                        ws.close();
                    }, 1000);
                }
            } catch (e) {
                console.log('📥 Raw message:', data.toString());
            }
        });
        
        ws.on('error', (error) => {
            console.error('❌ WebSocket error:', error.message);
        });
        
        ws.on('close', (code, reason) => {
            console.log(`🔌 Connection closed - Code: ${code}, Reason: ${reason.toString()}`);
            process.exit(0);
        });
        
    } catch (error) {
        console.error('❌ Connection failed:', error.message);
        process.exit(1);
    }
};

// Add timeout to prevent hanging
setTimeout(() => {
    console.log('⏰ Test timeout - exiting');
    process.exit(1);
}, 10000);

testWebSocket();
