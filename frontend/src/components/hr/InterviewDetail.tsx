import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { ArrowLeft, Calendar, User, Mail, Clock, FileText } from 'lucide-react';
import { toast } from 'sonner';
import type { Interview, Job } from '../../types';

interface InterviewDetailProps {
  interviewId: string;
  apiUrl: string;
}

export const InterviewDetail: React.FC<InterviewDetailProps> = ({ interviewId, apiUrl }) => {
  const navigate = useNavigate();
  const [interview, setInterview] = useState<Interview | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadInterview();
  }, [interviewId]);

  const loadInterview = async () => {
    try {
      setLoading(true);

      // Fetch interview details
      const interviewResponse = await fetch(`${apiUrl}/get_interview_by_id`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ interview_id: interviewId }),
      });
      const interviewData = await interviewResponse.json();

      if (interviewData.error) {
        toast.error(interviewData.error);
        return;
      }

      setInterview(interviewData.interview);

      // Fetch associated job details
      if (interviewData.interview.jobId) {
        const jobResponse = await fetch(`${apiUrl}/get_job_by_id`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ job_id: interviewData.interview.jobId }),
        });
        const jobData = await jobResponse.json();

        if (!jobData.error) {
          setJob(jobData.job);
        }
      }
    } catch (error) {
      toast.error('Failed to load interview details');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading interview details...</p>
        </div>
      </div>
    );
  }

  if (!interview) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle>Interview Not Found</CardTitle>
            <CardDescription>The interview you're looking for doesn't exist.</CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => navigate('/dashboard')}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const calculateDuration = () => {
    if (!interview.completedAt) return 'In Progress';

    const start = new Date(interview.startedAt);
    const end = new Date(interview.completedAt);
    const durationMs = end.getTime() - start.getTime();
    const minutes = Math.floor(durationMs / 60000);
    const seconds = Math.floor((durationMs % 60000) / 1000);

    return `${minutes}m ${seconds}s`;
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b">
        <div className="container mx-auto px-6 py-4">
          <Button variant="ghost" onClick={() => navigate('/dashboard')} className="mb-2">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Button>
          <h1 className="text-2xl font-bold">Interview Details</h1>
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-6 py-8 max-w-5xl">
        <div className="space-y-6">
          {/* Interview Status Card */}
          <Card>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-2xl">{interview.candidateName}</CardTitle>
                  <CardDescription>
                    {job?.title || 'Unknown Position'}
                  </CardDescription>
                </div>
                <Badge variant={interview.status === 'completed' ? 'default' : 'secondary'}>
                  {interview.status}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center gap-2">
                  <User className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm">
                    <span className="font-medium">Candidate:</span> {interview.candidateName}
                  </span>
                </div>

                {interview.candidateEmail && (
                  <div className="flex items-center gap-2">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">
                      <span className="font-medium">Email:</span> {interview.candidateEmail}
                    </span>
                  </div>
                )}

                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm">
                    <span className="font-medium">Started:</span> {formatDate(interview.startedAt)}
                  </span>
                </div>

                {interview.completedAt && (
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">
                      <span className="font-medium">Completed:</span> {formatDate(interview.completedAt)}
                    </span>
                  </div>
                )}

                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm">
                    <span className="font-medium">Duration:</span> {calculateDuration()}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Job Details Card */}
          {job && (
            <Card>
              <CardHeader>
                <CardTitle>Job Details</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <h3 className="font-semibold mb-1">{job.title}</h3>
                    <p className="text-sm text-muted-foreground">{job.description}</p>
                  </div>

                  <div>
                    <p className="text-sm font-medium mb-2">Required Skills:</p>
                    <div className="flex flex-wrap gap-2">
                      {job.skills.map((skill) => (
                        <Badge key={skill} variant="outline">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div className="flex gap-4">
                    <div>
                      <p className="text-sm font-medium">Difficulty:</p>
                      <Badge variant="secondary" className="mt-1">
                        {job.difficulty}
                      </Badge>
                    </div>
                    <div>
                      <p className="text-sm font-medium">Duration:</p>
                      <Badge variant="outline" className="mt-1">
                        {job.interviewDuration} minutes
                      </Badge>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Transcript Card */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                <CardTitle>Interview Transcript</CardTitle>
              </div>
              <CardDescription>
                {interview.transcript ? 'Full conversation transcript' : 'No transcript available'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {interview.transcript ? (
                <div className="bg-muted rounded-lg p-4">
                  <pre className="whitespace-pre-wrap text-sm font-mono">
                    {interview.transcript}
                  </pre>
                </div>
              ) : (
                <div className="text-center py-8">
                  <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
                  <p className="text-muted-foreground">
                    {interview.status === 'in_progress'
                      ? 'Transcript will be available once the interview is completed.'
                      : 'No transcript was recorded for this interview.'}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
