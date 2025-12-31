import React, { useEffect, useState } from 'react';
import './Dashboard.scss';

interface DashboardProps {
    onStartInterview: (topic: string) => void;
    onLogout: () => void;
    userId?: string;
    backendUrl?: string;
}

interface Interview {
    id: string;
    topic: string;
    timestamp: string;
    messages?: any[];
    durationSeconds?: number;
}

const TOPICS = [
    'System Design',
    'Python Algorithms',
    'Behavioral (STAR Method)',
    'Frontend Architecture',
    'Backend Scalability'
];

const Dashboard: React.FC<DashboardProps> = ({
    onStartInterview,
    onLogout,
    userId,
    backendUrl = "http://localhost:8000"
}) => {
    const [interviews, setInterviews] = useState<Interview[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchInterviews = async () => {
            if (!userId) {
                setLoading(false);
                return;
            }

            try {
                setLoading(true);
                setError(null);
                const response = await fetch(`${backendUrl}/get_user_interviews?user_id=${userId}&limit=10`);

                if (!response.ok) {
                    throw new Error(`Failed to fetch interviews: ${response.status}`);
                }

                const data = await response.json();
                setInterviews(data.interviews || []);
            } catch (err) {
                console.error('Error fetching interviews:', err);
                setError('Failed to load interview history');
            } finally {
                setLoading(false);
            }
        };

        fetchInterviews();
    }, [userId, backendUrl]);

    const formatDate = (timestamp: string) => {
        try {
            const date = new Date(timestamp);
            return date.toLocaleString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch {
            return timestamp;
        }
    };

    const formatDuration = (seconds?: number) => {
        if (!seconds) return 'N/A';
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}m ${secs}s`;
    };

    return (
        <div className="dashboard-container">
            <header>
                <h1>Interview Prep Dashboard</h1>
                <button onClick={onLogout} className="logout-btn">Logout</button>
            </header>

            <main>
                <section className="topics-section">
                    <h3>Select an Interview Topic</h3>
                    <div className="topics-grid">
                        {TOPICS.map((topic) => (
                            <div key={topic} className="topic-card" onClick={() => onStartInterview(topic)}>
                                <h4>{topic}</h4>
                                <p>Start a 30-min mock interview session.</p>
                            </div>
                        ))}
                    </div>
                </section>

                <section className="history-section">
                    <h3>Your Interview History</h3>
                    {loading && <p className="loading-message">Loading your interviews...</p>}
                    {error && <p className="error-message">{error}</p>}
                    {!loading && !error && interviews.length === 0 && (
                        <p className="empty-message">No interviews yet. Start your first one above!</p>
                    )}
                    {!loading && !error && interviews.length > 0 && (
                        <div className="interviews-list">
                            {interviews.map((interview) => (
                                <div key={interview.id} className="interview-card">
                                    <div className="interview-header">
                                        <h4>{interview.topic}</h4>
                                        <span className="interview-date">{formatDate(interview.timestamp)}</span>
                                    </div>
                                    <div className="interview-meta">
                                        <span className="meta-item">
                                            <strong>Duration:</strong> {formatDuration(interview.durationSeconds)}
                                        </span>
                                        <span className="meta-item">
                                            <strong>Messages:</strong> {interview.messages?.length || 0}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </section>
            </main>
        </div>
    );
};

export default Dashboard;
