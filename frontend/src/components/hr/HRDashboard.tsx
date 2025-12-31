import React, { useState, useEffect } from 'react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Copy, Check, Plus, Users, Bot, Info } from 'lucide-react';
import { JobForm } from './JobForm';
import { NavHeader } from '../NavHeader';
import { AgentDetailsDialog } from './AgentDetailsDialog';
import { toast } from 'sonner';
import type { Job, Interview, CreateJobRequest } from '../../types';

interface HRDashboardProps {
  userId: string;
  userEmail?: string;
  userName?: string;
  onLogout: () => void;
  apiUrl: string;
}

export const HRDashboard: React.FC<HRDashboardProps> = ({
  userId,
  userEmail,
  userName,
  onLogout,
  apiUrl
}) => {
  const [view, setView] = useState<'jobs' | 'create'>('jobs');
  const [jobs, setJobs] = useState<Job[]>([]);
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('jobs');
  const [selectedJobForAgent, setSelectedJobForAgent] = useState<Job | null>(null);

  useEffect(() => {
    loadJobs();
    loadInterviews();
  }, [userId]);

  const loadJobs = async () => {
    try {
      const response = await fetch(`${apiUrl}/get_jobs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId }),
      });
      const data = await response.json();
      if (data.jobs) {
        setJobs(data.jobs);
      }
    } catch (error) {
      toast.error('Failed to load jobs');
    }
  };

  const loadInterviews = async () => {
    try {
      const response = await fetch(`${apiUrl}/get_user_interviews_for_jobs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId }),
      });
      const data = await response.json();
      if (data.interviews) {
        setInterviews(data.interviews);
      }
    } catch (error) {
      toast.error('Failed to load interviews');
    }
  };

  const handleCreateJob = async (jobData: CreateJobRequest) => {
    setLoading(true);
    try {
      const response = await fetch(`${apiUrl}/create_job`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, job_data: jobData }),
      });
      const data = await response.json();
      if (data.status === 'success') {
        if (data.agentId) {
          toast.success('Job created with dedicated AI agent!');
        } else {
          toast.success('Job created successfully!');
        }
        setView('jobs');
        loadJobs();
      } else {
        toast.error(data.error || 'Failed to create job');
      }
    } catch (error) {
      toast.error('Failed to create job');
    } finally {
      setLoading(false);
    }
  };

  const copyShareLink = (shareToken: string) => {
    const shareUrl = `${window.location.origin}/interview/${shareToken}`;
    navigator.clipboard.writeText(shareUrl);
    setCopied(shareToken);
    toast.success('Link copied to clipboard!');
    setTimeout(() => setCopied(null), 2000);
  };

  const getInterviewCount = (jobId: string) => {
    return interviews.filter((i) => i.jobId === jobId).length;
  };

  if (view === 'create') {
    return (
      <div className="min-h-screen bg-background">
        <NavHeader
          userName={userName}
          userEmail={userEmail}
          onLogout={onLogout}
          activeTab={activeTab}
          onTabChange={setActiveTab}
        />
        <div className="p-6">
          <JobForm
            onSubmit={handleCreateJob}
            onCancel={() => setView('jobs')}
            loading={loading}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation Header */}
      <NavHeader
        userName={userName}
        userEmail={userEmail}
        onLogout={onLogout}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      {/* Content */}
      <div className="container mx-auto px-6 py-8">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-3xl font-bold">My Jobs</h2>
            <p className="text-muted-foreground mt-1">
              Create job postings and share interview links with candidates
            </p>
          </div>
          <Button onClick={() => setView('create')}>
            <Plus className="h-4 w-4 mr-2" />
            Create Job
          </Button>
        </div>

        {/* Jobs List */}
        {jobs.length === 0 ? (
          <Card className="p-12 text-center">
            <div className="flex flex-col items-center gap-4">
              <div className="h-16 w-16 rounded-full bg-muted flex items-center justify-center">
                <Users className="h-8 w-8 text-muted-foreground" />
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-2">No jobs yet</h3>
                <p className="text-muted-foreground mb-4">
                  Create your first job posting to start screening candidates
                </p>
                <Button onClick={() => setView('create')}>
                  <Plus className="h-4 w-4 mr-2" />
                  Create Your First Job
                </Button>
              </div>
            </div>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {jobs.map((job) => (
              <Card key={job.id} className="flex flex-col">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <CardTitle className="text-lg mb-2">{job.title}</CardTitle>
                      <div className="flex gap-2 mb-2 flex-wrap">
                        <Badge variant="secondary">{job.difficulty}</Badge>
                        <Badge variant="outline">{job.interviewDuration} min</Badge>
                        {job.agentId && (
                          <Badge variant="default" className="flex items-center gap-1">
                            <Bot className="h-3 w-3" />
                            Dedicated AI
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                  <CardDescription className="line-clamp-2">{job.description}</CardDescription>
                </CardHeader>
                <CardContent className="flex-1">
                  <div className="space-y-3">
                    <div>
                      <p className="text-sm font-medium mb-1">Required Skills:</p>
                      <div className="flex flex-wrap gap-1">
                        {job.skills.map((skill) => (
                          <Badge key={skill} variant="outline" className="text-xs">
                            {skill}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Users className="h-4 w-4" />
                      <span>{getInterviewCount(job.id)} interviews</span>
                    </div>

                    {job.agentId && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="w-full justify-start text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedJobForAgent(job);
                        }}
                      >
                        <Info className="h-4 w-4 mr-2" />
                        View AI Agent Details
                      </Button>
                    )}

                    <Button
                      variant="outline"
                      className="w-full"
                      onClick={(e) => {
                        e.stopPropagation();
                        copyShareLink(job.shareToken);
                      }}
                    >
                      {copied === job.shareToken ? (
                        <>
                          <Check className="h-4 w-4 mr-2" />
                          Copied!
                        </>
                      ) : (
                        <>
                          <Copy className="h-4 w-4 mr-2" />
                          Copy Interview Link
                        </>
                      )}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Interviews Section */}
        {interviews.length > 0 && (
          <div className="mt-12">
            <h3 className="text-2xl font-bold mb-4">Recent Interviews</h3>
            <div className="grid gap-4">
              {interviews.slice(0, 10).map((interview) => {
                const job = jobs.find((j) => j.id === interview.jobId);
                return (
                  <Card
                    key={interview.id}
                    className="hover:shadow-md transition-shadow cursor-pointer"
                    onClick={() => (window.location.href = `/interview-detail/${interview.id}`)}
                  >
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <CardTitle className="text-base">{interview.candidateName}</CardTitle>
                          <CardDescription>
                            {job?.title || 'Unknown Job'} •{' '}
                            {new Date(interview.startedAt).toLocaleDateString()}
                            {interview.candidateEmail && ` • ${interview.candidateEmail}`}
                          </CardDescription>
                          {interview.transcript && (
                            <p className="text-sm text-muted-foreground mt-2 line-clamp-2">
                              {interview.transcript.substring(0, 150)}...
                            </p>
                          )}
                        </div>
                        <Badge variant={interview.status === 'completed' ? 'default' : 'secondary'}>
                          {interview.status}
                        </Badge>
                      </div>
                    </CardHeader>
                  </Card>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Agent Details Dialog */}
      {selectedJobForAgent && (
        <AgentDetailsDialog
          job={selectedJobForAgent}
          open={!!selectedJobForAgent}
          onOpenChange={(open) => !open && setSelectedJobForAgent(null)}
        />
      )}
    </div>
  );
};
