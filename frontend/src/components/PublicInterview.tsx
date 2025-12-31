import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import { Briefcase, Clock, TrendingUp } from 'lucide-react';
import { toast } from 'sonner';
import Interview from './Interview';
import type { Job } from '../types';

interface PublicInterviewProps {
  apiUrl: string;
}

export const PublicInterview: React.FC<PublicInterviewProps> = ({ apiUrl }) => {
  const { shareToken } = useParams<{ shareToken: string }>();
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [stage, setStage] = useState<'info' | 'form' | 'interview' | 'complete'>('info');
  const [candidateName, setCandidateName] = useState('');
  const [candidateEmail, setCandidateEmail] = useState('');
  const [interviewId, setInterviewId] = useState('');

  useEffect(() => {
    loadJob();
  }, [shareToken]);

  const loadJob = async () => {
    if (!shareToken) {
      toast.error('Invalid interview link');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${apiUrl}/get_job_by_token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ share_token: shareToken }),
      });
      const data = await response.json();

      if (data.error) {
        toast.error(data.error);
        setLoading(false);
        return;
      }

      if (data.job) {
        setJob(data.job);
        setStage('form');
      }
    } catch (error) {
      toast.error('Failed to load job details');
    } finally {
      setLoading(false);
    }
  };

  const handleStartInterview = async () => {
    if (!candidateName.trim()) {
      toast.error('Please enter your name');
      return;
    }

    if (!job) return;

    setLoading(true);
    try {
      // Create interview record
      const response = await fetch(`${apiUrl}/create_interview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          interview_data: {
            jobId: job.id,
            candidateName: candidateName.trim(),
            candidateEmail: candidateEmail.trim() || undefined,
            shareToken,
          },
        }),
      });
      const data = await response.json();

      if (data.status === 'success') {
        setInterviewId(data.id);
        setStage('interview');
      } else {
        toast.error(data.error || 'Failed to start interview');
      }
    } catch (error) {
      toast.error('Failed to start interview');
    } finally {
      setLoading(false);
    }
  };

  const handleInterviewEnd = async (transcript?: string) => {
    if (!interviewId) return;

    try {
      // Update interview with completion status and transcript
      await fetch(`${apiUrl}/update_interview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          interview_id: interviewId,
          updates: {
            status: 'completed',
            transcript: transcript || '',
            completedAt: new Date().toISOString(),
          },
        }),
      });

      setStage('complete');
    } catch (error) {
      toast.error('Failed to save interview');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <p>Loading...</p>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-6">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle>Invalid Link</CardTitle>
            <CardDescription>
              This interview link is invalid or has expired. Please contact the recruiter for a new link.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    );
  }

  if (stage === 'form') {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-6">
        <Card className="max-w-2xl w-full">
          <CardHeader>
            <CardTitle className="text-2xl">{job.title}</CardTitle>
            <CardDescription>AI-Powered Screening Interview</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Job Details */}
            <div>
              <h3 className="font-semibold mb-2">About this position:</h3>
              <p className="text-sm text-muted-foreground">{job.description}</p>
            </div>

            <div className="flex flex-wrap gap-4">
              <div className="flex items-center gap-2 text-sm">
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
                <span className="capitalize">{job.difficulty} Level</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Clock className="h-4 w-4 text-muted-foreground" />
                <span>{job.interviewDuration} minutes</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Briefcase className="h-4 w-4 text-muted-foreground" />
                <span>{job.skills.length} required skills</span>
              </div>
            </div>

            <div>
              <h3 className="font-semibold mb-2">Required Skills:</h3>
              <div className="flex flex-wrap gap-2">
                {job.skills.map((skill) => (
                  <Badge key={skill} variant="secondary">
                    {skill}
                  </Badge>
                ))}
              </div>
            </div>

            <div className="border-t pt-4">
              <h3 className="font-semibold mb-4">Enter your details to begin:</h3>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Full Name *</Label>
                  <Input
                    id="name"
                    value={candidateName}
                    onChange={(e) => setCandidateName(e.target.value)}
                    placeholder="John Doe"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email (Optional)</Label>
                  <Input
                    id="email"
                    type="email"
                    value={candidateEmail}
                    onChange={(e) => setCandidateEmail(e.target.value)}
                    placeholder="john@example.com"
                  />
                </div>
              </div>
            </div>

            <div className="bg-muted p-4 rounded-lg">
              <h4 className="font-semibold mb-2">What to expect:</h4>
              <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                <li>Voice-based conversation with an AI interviewer</li>
                <li>Questions tailored to the {job.title} role</li>
                <li>Duration: approximately {job.interviewDuration} minutes</li>
                <li>Results will be shared with the hiring team</li>
              </ul>
            </div>

            <Button
              onClick={handleStartInterview}
              disabled={loading || !candidateName.trim()}
              className="w-full"
              size="lg"
            >
              {loading ? 'Starting Interview...' : 'Start Interview'}
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (stage === 'interview') {
    return (
      <div className="min-h-screen bg-background">
        <Interview
          topic={`${job.title} Interview`}
          jobId={job.id}
          candidateName={candidateName}
          onEndInterview={handleInterviewEnd}
          userId="" // Not needed for public interviews
        />
      </div>
    );
  }

  if (stage === 'complete') {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-6">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle>Interview Completed!</CardTitle>
            <CardDescription>Thank you for your time, {candidateName}.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Your interview has been successfully submitted. The hiring team will review your
              responses and be in touch soon.
            </p>
            <div className="bg-muted p-4 rounded-lg">
              <p className="text-sm font-medium">What happens next?</p>
              <ul className="text-sm text-muted-foreground mt-2 space-y-1 list-disc list-inside">
                <li>The hiring team will review your interview</li>
                <li>You'll hear back within 5-7 business days</li>
                <li>Check your email for updates</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return null;
};
