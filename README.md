Inspiration
Traditional hiring processes are time-consuming, expensive, and often inconsistent. HR teams spend countless hours conducting initial screening interviews, while candidates struggle to find convenient interview times across time zones. We were inspired to democratize access to quality job screening by creating an AI-powered interview platform that:

Scales instantly to screen hundreds of candidates simultaneously
Provides consistent, unbiased initial assessments
Works 24/7 across all time zones
Frees HR teams to focus on final-stage interviews and relationship building
We envisioned a marketplace where gig workers, freelancers, and job seekers could get instant, professional interview experiences, while employers could efficiently screen talent at scale.

## What it does

Gig Bazar AI Interviewer is a voice-based AI interview platform with two sides:

For HR/Employers:

Create detailed job postings with required skills, experience level, and interview duration
Automatically generate a dedicated AI interviewer agent for each position
Customize AI instructions (e.g., "focus on system design" or "assess leadership skills")
Share interview links via email, social media, or job boards
Review full interview transcripts with candidate details
Track all interviews from a centralized dashboard
For Candidates:

Click a shareable link - no account needed
See complete job details before starting
Have natural voice conversations with an AI interviewer tailored to the specific role
Experience structured interviews covering technical skills, behavioral questions, and Q&A
Complete interviews on their own schedule, anywhere in the world
The AI adapts every interview based on:

Job requirements and skills
Seniority level (junior/mid/senior)
Custom HR instructions
Candidate responses in real-time
## How we built it

### Frontend (React + TypeScript):

Built responsive UI with React and TypeScript for type safety
Integrated shadcn/ui components for a polished, professional interface
Implemented routing for HR dashboard, job creation, and public interview pages
Used Tailwind CSS for rapid, consistent styling
Connected to ElevenLabs Web SDK for real-time voice interactions
### Backend (Python + FastAPI):

Created RESTful API with FastAPI for high performance
Built modular services: job_service.py, interview_service.py, elevenlabs_service.py
Implemented dynamic prompt generation that adapts to each job's requirements
Automated ElevenLabs agent creation using their Conversational AI API
Integrated Firebase Authentication and Firestore database
AI Integration:

Integrated ElevenLabs Conversational AI for natural voice interactions
Designed comprehensive interview prompts with structured flow (opening → technical → behavioral → Q&A → closing)
Created automatic agent provisioning - each job gets its own dedicated AI interviewer
Built dynamic prompt system incorporating job details, skills, difficulty, and custom instructions
## Infrastructure:

Deployed on Google Cloud Platform
Used Firestore for real-time data synchronization
Implemented shareable token system for public interview access
Structured database schema for scalable multi-tenant architecture
## Challenges we ran into

Dynamic Prompt Engineering: Creating a single prompt template that works for junior developers, senior architects, and everything in between required extensive iteration. We solved this by building a modular prompt system that adapts based on role requirements.
Real-time Voice Latency: Initial implementations had noticeable delays in AI responses. We optimized by using ElevenLabs' low-latency conversational agents and implementing proper audio streaming.
Agent Lifecycle Management: Deciding when to create, update, and delete AI agents for jobs. We implemented automatic creation on job posting and added manual management endpoints for flexibility.
Transcript Storage & Retrieval: Handling potentially long interview transcripts efficiently in Firestore required careful schema design to balance query performance and cost.
Public vs. Authenticated Routes: Balancing security (HR dashboard) with accessibility (public interview links) required careful authentication flow design.
SDK Version Compatibility: ElevenLabs SDK updates required graceful error handling to ensure the system continues working even with API changes.
## Accomplishments that we're proud of

✅ End-to-End Working MVP: Built a complete, functional platform in hackathon timeframe ✅ Automatic AI Agent Creation: Seamless per-job agent provisioning with zero manual intervention ✅ Beautiful, Intuitive UI: Professional interface using shadcn/ui that rivals commercial products ✅ Natural Voice Conversations: Achieved smooth, low-latency AI interviews that feel human ✅ Scalable Architecture: Designed for thousands of concurrent interviews ✅ Zero Candidate Friction: No account creation - just click and interview ✅ Full Visibility: HR sees complete transcripts with timestamps and candidate information ✅ Extensible Design: Built modular services ready for marketplace features

## What we learned

## Technical Learnings:

Real-time voice AI requires careful latency optimization and error handling
Dynamic prompt engineering is an art - small changes dramatically affect interview quality
Firebase + React is incredibly powerful for rapid MVP development
TypeScript prevents countless bugs in complex React applications
Modular service architecture makes features easy to add and test
## Product Learnings:

HR users need customization but not overwhelming options
Candidates prefer no-friction experiences (no signup) over personalized accounts
Transcript visibility is more valuable to HR than automated scoring in early stages
Shareable links are the killer feature for distribution
## AI Learnings:

Conversational AI works best with clear structure (opening, technical, closing)
Custom instructions should guide, not override, base interview best practices
Voice-based screening reveals communication skills that text-based systems miss
## What's next for Gig Bazar AI Interviewer

Immediate Enhancements:

AI-Powered Candidate Scoring: Automatic evaluation based on technical accuracy, communication clarity, and role fit
Email Notifications: Auto-send interview invites and transcripts
Interview Analytics: Dashboard showing candidate performance metrics, time-to-complete, and drop-off rates
Candidate Accounts: Let candidates track their interview history and results
Marketplace Expansion:

Gig/Freelance Matching: Extend beyond interviews to full job/gig marketplace
Multi-Organization Support: White-label solution for recruitment agencies
Video Support: Add visual component for roles requiring presentation skills
Interview Scheduling: Calendar integration for hybrid AI + human interview workflows
Payment Integration: Monetize through per-interview or subscription models
Advanced AI Features:

Personality Assessment: Integrate psychometric evaluation
Code Challenge Integration: Live coding assessments during voice interviews
Multi-Language Support: Conduct interviews in candidate's preferred language
Interview Templates: Pre-built agents for common roles (SWE, PM, Designer)
Enterprise Features:

HRIS Integration: Connect with Workday, Greenhouse, Lever
Compliance & Privacy: GDPR, SOC2, candidate data management
Collaboration Tools: Multi-reviewer workflows, shared notes, hiring committees
Our vision: Become the default pre-screening layer for every job posting worldwide - making hiring faster, fairer, and more accessible for everyone.