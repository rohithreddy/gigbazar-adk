export type DifficultyLevel = 'junior' | 'mid' | 'senior';
export type InterviewDuration = 5 | 10 | 15;

export interface Job {
  id: string;
  createdBy: string;
  title: string;
  description: string;
  skills: string[];
  difficulty: DifficultyLevel;
  interviewDuration: InterviewDuration;
  customPrompt?: string;
  shareToken: string;
  createdAt: string;
  agentId?: string;
  agentName?: string;
  agentCreatedAt?: string;
  agentVoiceId?: string;
  agentLanguage?: string;
}

export interface Interview {
  id: string;
  jobId: string;
  candidateName: string;
  candidateEmail?: string;
  status: 'in_progress' | 'completed';
  startedAt: string;
  completedAt?: string;
  transcript: string;
  elevenlabsConversationId?: string;
}

export interface CreateJobRequest {
  title: string;
  description: string;
  skills: string[];
  difficulty: DifficultyLevel;
  interviewDuration: InterviewDuration;
  customPrompt?: string;
}

export interface CreateInterviewRequest {
  jobId: string;
  candidateName: string;
  candidateEmail?: string;
  shareToken: string;
}

export interface User {
  id: string;
  email: string;
  role: 'hr';
  createdAt: string;
}
