import React, { useCallback, useState, useRef } from 'react';
/* 
    This library uses the ElevenLabs Conversational AI SDK for React.
    It allows us to have granular control over the conversation flow (Start, End).
*/
import { useConversation } from '@elevenlabs/react';
import './Interview.scss';

interface InterviewProps {
    topic: string;
    onEndInterview: () => void;
    // Assuming backend is at localhost:8000 by default for now, can be configured
    backendUrl?: string;
    userId?: string;
}

const Interview: React.FC<InterviewProps> = ({ topic, onEndInterview, backendUrl = "http://localhost:8000", userId }) => {
    // Track messages for persistence
    const [messages, setMessages] = useState<any[]>([]);
    // Use a ref to access latest messages in callbacks without re-creating them
    const messagesRef = useRef<any[]>([]);

    const conversation = useConversation({
        onConnect: () => console.log('Connected'),
        onDisconnect: () => console.log('Disconnected'),
        onMessage: (message: any) => {
            console.log('Message:', message);
            // Append incoming message to our transcript
            const newMsg = { ...message, timestamp: new Date().toISOString() };
            setMessages(prev => {
                const updated = [...prev, newMsg];
                messagesRef.current = updated;
                return updated;
            });
        },
        onError: (error: any) => console.error('Error:', error),
    });

    const startConversation = useCallback(async () => {
        try {
            // Request microphone permission explicitly
            await navigator.mediaDevices.getUserMedia({ audio: true });

            const agentId = 'agent_1301kdn9m60af3jawwhtacys4z4v'; // YOUR_AGENT_ID

            // Fetch signed URL from backend
            let signedUrl = null;
            try {
                // Construct the HTTP URL from the backendUrl (handling potential ws:// prefix if passed from context later)
                const httpUrl = backendUrl.replace('ws', 'http');
                const response = await fetch(`${httpUrl}/get_elevenlabs_signed_url`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ agent_id: agentId })
                });

                if (response.ok) {
                    const data = await response.json();
                    if (data.signed_url) {
                        signedUrl = data.signed_url;
                    } else if (data.error) {
                        console.warn('Backend returned error for signed URL:', data.error);
                    }
                } else {
                    console.warn('Failed to fetch signed URL, falling back to public agent ID. Status:', response.status);
                }
            } catch (backendError) {
                console.warn('Error connecting to backend for signed URL, falling back:', backendError);
            }

            // Start the conversation
            if (signedUrl) {
                console.log('Starting session with Signed URL');
                await conversation.startSession({
                    signedUrl: signedUrl,
                    // signedUrl typically works with websocket. Explicitly setting it or letting it default.
                    // @ts-ignore - types might be strict
                    connectionType: 'websocket',
                });
            } else {
                console.log('Starting session with Agent ID (Fallback)');
                await conversation.startSession({
                    agentId: agentId,
                    // @ts-ignore
                    connectionType: 'webrtc',
                });
            }

        } catch (error) {
            console.error('Failed to start conversation:', error);
            alert('Failed to start conversation. Please check microphone permissions and backend connection.');
        }
    }, [conversation, backendUrl]);

    const stopConversation = useCallback(async () => {
        await conversation.endSession();

        // Save session data to backend
        try {
            const httpUrl = backendUrl.replace('ws', 'http');
            const sessionData = {
                topic,
                timestamp: new Date().toISOString(),
                messages: messagesRef.current,
                durationSeconds: 0,
                userId: userId || 'anonymous',
            };

            console.log('Saving interview data:', sessionData);

            await fetch(`${httpUrl}/save_interview_data`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(sessionData)
            });

            // Clear messages for next time if needed, or leave them for display
            // setMessages([]); 
            // messagesRef.current = [];
        } catch (err) {
            console.error('Failed to save interview data:', err);
        }

    }, [conversation, backendUrl, topic]);

    const isConnected = conversation.status === 'connected';
    const isConnecting = conversation.status === 'connecting';

    return (
        <div className="interview-container">
            <header>
                <h2>Mock Interview: {topic}</h2>
                <div className="header-actions">
                    <button onClick={onEndInterview} className="end-btn secondary">Back to Dashboard</button>
                </div>
            </header>

            <div className="avatar-container">
                <div className={`status-indicator ${conversation.status}`}>
                    {conversation.status === 'connected' ? 'Listening...' :
                        conversation.status === 'connecting' ? 'Connecting...' : 'Ready to Start'}
                </div>

                <div className="call-controls">
                    {!isConnected && (
                        <button
                            onClick={startConversation}
                            disabled={isConnecting}
                            className={`call-btn ${isConnecting ? 'loading' : ''}`}
                        >
                            {isConnecting ? 'Connecting...' : 'Start Interview Call'}
                        </button>
                    )}

                    {isConnected && (
                        <button onClick={stopConversation} className="end-call-btn">
                            End Call
                        </button>
                    )}
                </div>
            </div>

            <div className="instructions">
                <p>
                    <strong>Instructions:</strong> speak clearly into your microphone after clicking "Start Interview Call".
                    The AI Interviewer will conduct the session based on the topic "{topic}".
                </p>
                <p className="note">
                    Note: This uses the ElevenLabs React SDK for custom control.
                </p>
            </div>
        </div>
    );
};

export default Interview;
