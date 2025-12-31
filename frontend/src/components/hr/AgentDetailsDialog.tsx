import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
import { Badge } from '../ui/badge';
import { Card, CardContent } from '../ui/card';
import { Bot, Calendar, Volume2, Globe, Sparkles, CheckCircle2 } from 'lucide-react';
import type { Job } from '../../types';

interface AgentDetailsDialogProps {
  job: Job;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const AgentDetailsDialog: React.FC<AgentDetailsDialogProps> = ({
  job,
  open,
  onOpenChange,
}) => {
  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getVoiceName = (voiceId?: string) => {
    const voices: Record<string, string> = {
      '21m00Tcm4TlvDq8ikWAM': 'Rachel (Default)',
      'EXAVITQu4vr4xnSDxMaL': 'Sarah',
      'TxGEqnHWrfWFTfGW9XjX': 'Josh',
      // Add more as needed
    };
    return voices[voiceId || ''] || voiceId || 'Default Voice';
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center gap-3">
            <div className="h-12 w-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <Bot className="h-6 w-6 text-white" />
            </div>
            <div>
              <DialogTitle className="text-xl">AI Agent Details</DialogTitle>
              <DialogDescription>
                Dedicated interviewer for {job.title}
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-4 mt-4">
          {/* Status Card */}
          <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 text-green-700">
                <CheckCircle2 className="h-5 w-5" />
                <span className="font-semibold">Active & Ready</span>
              </div>
              <p className="text-sm text-green-600 mt-1">
                This AI agent is configured and ready to conduct interviews
              </p>
            </CardContent>
          </Card>

          {/* Agent Information */}
          <Card>
            <CardContent className="pt-6 space-y-4">
              <div>
                <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground mb-2">
                  <Sparkles className="h-4 w-4" />
                  Agent Name
                </div>
                <p className="text-base font-semibold">{job.agentName || 'N/A'}</p>
              </div>

              <div>
                <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground mb-2">
                  <Bot className="h-4 w-4" />
                  Agent ID
                </div>
                <p className="text-sm font-mono bg-muted px-3 py-2 rounded">
                  {job.agentId || 'N/A'}
                </p>
              </div>

              <div>
                <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground mb-2">
                  <Calendar className="h-4 w-4" />
                  Created
                </div>
                <p className="text-sm">{formatDate(job.agentCreatedAt)}</p>
              </div>

              <div>
                <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground mb-2">
                  <Volume2 className="h-4 w-4" />
                  Voice
                </div>
                <Badge variant="secondary">{getVoiceName(job.agentVoiceId)}</Badge>
              </div>

              <div>
                <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground mb-2">
                  <Globe className="h-4 w-4" />
                  Language
                </div>
                <Badge variant="outline">
                  {job.agentLanguage?.toUpperCase() || 'EN'}
                </Badge>
              </div>
            </CardContent>
          </Card>

          {/* Job Context */}
          <Card>
            <CardContent className="pt-6 space-y-4">
              <div>
                <h4 className="text-sm font-semibold mb-2">Position</h4>
                <p className="text-base">{job.title}</p>
              </div>

              <div>
                <h4 className="text-sm font-semibold mb-2">Required Skills</h4>
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
                  <h4 className="text-sm font-semibold mb-2">Experience Level</h4>
                  <Badge variant="secondary" className="capitalize">
                    {job.difficulty}
                  </Badge>
                </div>
                <div>
                  <h4 className="text-sm font-semibold mb-2">Duration</h4>
                  <Badge variant="outline">{job.interviewDuration} minutes</Badge>
                </div>
              </div>

              {job.customPrompt && (
                <div>
                  <h4 className="text-sm font-semibold mb-2">Custom Instructions</h4>
                  <p className="text-sm text-muted-foreground bg-muted px-3 py-2 rounded whitespace-pre-wrap">
                    {job.customPrompt}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* How It Works */}
          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="pt-6">
              <h4 className="text-sm font-semibold text-blue-900 mb-3">
                How This Agent Works
              </h4>
              <ul className="space-y-2 text-sm text-blue-800">
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 mt-0.5">•</span>
                  <span>
                    Conducts interviews based on the job requirements and your custom
                    instructions
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 mt-0.5">•</span>
                  <span>
                    Asks tailored questions about {job.skills.join(', ')} and evaluates{' '}
                    {job.difficulty}-level expertise
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 mt-0.5">•</span>
                  <span>
                    Maintains professional conversation for {job.interviewDuration} minutes
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 mt-0.5">•</span>
                  <span>Generates complete transcripts for your review</span>
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </DialogContent>
    </Dialog>
  );
};
