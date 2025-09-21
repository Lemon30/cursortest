# CV-Job Matching API - Product Requirements Document

## 1. Executive Summary

The CV-Job Matching API is a backend service that analyzes the compatibility between a candidate's CV and LinkedIn job postings using AI-powered analysis. The system leverages OpenAI's GPT models to provide intelligent matching scores and detailed feedback on job fit.

### Vision
To create an automated, intelligent system that helps job seekers quickly assess their compatibility with job opportunities, saving time and improving application success rates.

### Success Metrics
- **Match Accuracy**: 85%+ correlation with human recruiter assessments
- **Response Time**: < 5 seconds for analysis completion
- **User Satisfaction**: 4.5+ star rating from beta users
- **API Uptime**: 99.9% availability

## 2. Product Overview

### Core Functionality
The API accepts a candidate's CV (resume) and a LinkedIn job post URL, then returns a comprehensive analysis including:
- Overall match percentage (0-100%)
- Detailed skill gap analysis
- Strengths alignment
- Improvement recommendations
- Key missing qualifications

### Target Users
- **Primary**: Job seekers and career professionals
- **Secondary**: Recruitment agencies and HR departments
- **Tertiary**: Career coaching platforms and job boards

## 3. Functional Requirements

### 3.1 Core Features

#### FR-001: CV Analysis Endpoint
**Description**: Accept CV files and extract relevant information for analysis
- **Input**: CV file (PDF, DOC, DOCX, TXT) or raw text
- **Processing**: Extract skills, experience, education, certifications
- **Output**: Structured CV data for matching analysis

#### FR-002: LinkedIn Job Post Analysis
**Description**: Extract and analyze job requirements from LinkedIn URLs
- **Input**: LinkedIn job post URL
- **Processing**: Web scraping/API integration to extract job details
- **Output**: Structured job requirements data

#### FR-003: AI-Powered Matching Analysis
**Description**: Generate compatibility analysis using OpenAI GPT models
- **Input**: Structured CV data + Job requirements
- **Processing**: AI analysis comparing qualifications vs requirements
- **Output**: Detailed match report with scores and recommendations

#### FR-004: Match Score Calculation
**Description**: Generate numerical match percentage with breakdown
- **Components**:
  - Skills match (40% weight)
  - Experience relevance (30% weight)
  - Education alignment (15% weight)
  - Industry fit (10% weight)
  - Location compatibility (5% weight)

### 3.2 API Endpoints

#### POST /analyze-match
Primary endpoint for CV-job matching analysis

**Request Body:**
```json
{
  "cv": {
    "file_url": "string (optional)",
    "text_content": "string (optional)",
    "file_base64": "string (optional)"
  },
  "job_url": "string (required)",
  "analysis_depth": "basic|detailed|comprehensive (optional, default: detailed)"
}
```

**Response:**
```json
{
  "match_id": "uuid",
  "overall_score": 85,
  "analysis": {
    "skills": {
      "matched": ["Python", "FastAPI", "Docker"],
      "missing": ["Kubernetes", "GraphQL"],
      "score": 78
    },
    "experience": {
      "relevance_score": 92,
      "years_match": true,
      "industry_alignment": "high"
    },
    "education": {
      "requirement_met": true,
      "score": 95
    },
    "strengths": [
      "Strong backend development experience",
      "Relevant cloud platform knowledge"
    ],
    "gaps": [
      "Limited experience with microservices architecture",
      "No GraphQL experience mentioned"
    ],
    "recommendations": [
      "Consider learning Kubernetes for container orchestration",
      "Highlight your API development experience more prominently"
    ]
  },
  "processing_time_ms": 3245,
  "timestamp": "2025-09-21T10:30:00Z"
}
```

#### GET /match-history/{match_id}
Retrieve previous analysis results

#### POST /cv/upload
Upload and validate CV files

#### GET /supported-formats
List supported CV file formats and LinkedIn URL patterns

#### GET /health
Health check endpoint

### 3.3 Data Processing Requirements

#### CV Processing
- **File Support**: PDF, DOC, DOCX, TXT formats
- **Text Extraction**: OCR for scanned documents
- **Data Parsing**: Extract structured information (skills, experience, education)
- **Privacy**: No CV data stored permanently after analysis

#### LinkedIn Integration
- **URL Validation**: Verify LinkedIn job post URLs
- **Content Extraction**: Job title, requirements, company info, location
- **Rate Limiting**: Respect LinkedIn's robots.txt and rate limits
- **Caching**: Cache job post data for 24 hours to reduce scraping

## 4. Non-Functional Requirements

### 4.1 Performance
- **Response Time**: 95% of requests processed within 5 seconds
- **Throughput**: Support 100 concurrent requests
- **Scalability**: Horizontal scaling capability

### 4.2 Security
- **Data Privacy**: CV content not stored after analysis
- **API Authentication**: JWT-based authentication
- **Rate Limiting**: 100 requests per hour per user
- **Input Validation**: Comprehensive request validation

### 4.3 Reliability
- **Uptime**: 99.9% availability SLA
- **Error Handling**: Graceful degradation and detailed error messages
- **Monitoring**: Health checks and performance metrics
- **Backup**: Redundant processing capabilities

### 4.4 Compliance
- **GDPR**: EU data protection compliance
- **CCPA**: California privacy law compliance
- **SOC 2**: Security and availability standards

## 5. Technical Architecture

### 5.1 Technology Stack
- **Backend Framework**: FastAPI (Python)
- **AI Integration**: OpenAI GPT-4 API
- **Document Processing**: PyPDF2, python-docx, pytesseract
- **Web Scraping**: BeautifulSoup4, Selenium (as fallback)
- **Database**: PostgreSQL (for analytics and caching)
- **Cache**: Redis (for job post caching)
- **Deployment**: Docker containers on AWS/GCP

### 5.2 System Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   API Gateway   │────│   FastAPI App    │────│   OpenAI API    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                       ┌────────┴────────┐
                       │                 │
              ┌─────────────────┐ ┌─────────────────┐
              │  CV Processor   │ │  Job Scraper    │
              └─────────────────┘ └─────────────────┘
                       │                 │
              ┌─────────────────┐ ┌─────────────────┐
              │   PostgreSQL    │ │     Redis       │
              │   (Analytics)   │ │   (Caching)     │
              └─────────────────┘ └─────────────────┘
```

### 5.3 Data Flow
1. **Request Reception**: API receives CV and LinkedIn URL
2. **CV Processing**: Extract and structure CV content
3. **Job Analysis**: Scrape and parse LinkedIn job post
4. **AI Analysis**: Send structured data to OpenAI for matching
5. **Score Calculation**: Process AI response into match scores
6. **Response Generation**: Return formatted analysis to client

## 6. Integration Requirements

### 6.1 External APIs
- **OpenAI API**: GPT-4 for intelligent analysis
- **LinkedIn**: Job post content extraction
- **File Storage**: AWS S3 or Google Cloud Storage (temporary)

### 6.2 Third-Party Libraries
- **Document Processing**: PyPDF2, python-docx, pytesseract
- **Web Scraping**: requests, BeautifulSoup4, Selenium
- **ML/NLP**: spaCy or NLTK for text preprocessing

## 7. Development Phases

### Phase 1: MVP (4 weeks)
- [ ] Basic CV text analysis
- [ ] LinkedIn URL job extraction
- [ ] Simple OpenAI integration
- [ ] Core matching algorithm
- [ ] Basic API endpoints

### Phase 2: Enhanced Features (3 weeks)
- [ ] File upload support (PDF, DOC)
- [ ] Advanced skill extraction
- [ ] Detailed scoring breakdown
- [ ] Caching implementation
- [ ] Error handling improvements

### Phase 3: Production Ready (3 weeks)
- [ ] Authentication system
- [ ] Rate limiting
- [ ] Monitoring and logging
- [ ] Performance optimization
- [ ] Security hardening

### Phase 4: Advanced Features (4 weeks)
- [ ] Match history tracking
- [ ] Batch processing
- [ ] Custom scoring weights
- [ ] Integration APIs
- [ ] Analytics dashboard

## 8. Success Criteria

### 8.1 Technical Metrics
- API response time < 5 seconds (95th percentile)
- 99.9% uptime
- Zero data breaches
- 100% test coverage for core functionality

### 8.2 Business Metrics
- 85%+ user satisfaction rating
- 1000+ successful analyses per month
- 10+ enterprise integration partners
- 90%+ accuracy in match predictions

## 9. Risk Assessment

### 9.1 Technical Risks
- **LinkedIn Anti-Scraping**: Mitigation through respectful scraping and API alternatives
- **OpenAI Rate Limits**: Implement request queuing and retry logic
- **CV Format Variations**: Extensive testing with diverse CV formats

### 9.2 Business Risks
- **Privacy Concerns**: Implement strong data protection measures
- **Competition**: Focus on superior accuracy and user experience
- **Scalability**: Design for horizontal scaling from day one

## 10. Appendix

### 10.1 API Error Codes
- `400`: Invalid request format
- `401`: Authentication required
- `403`: Rate limit exceeded
- `422`: CV processing failed
- `429`: LinkedIn scraping rate limited
- `500`: Internal server error
- `503`: OpenAI service unavailable

### 10.2 Supported CV Formats
- PDF (text-based and scanned)
- Microsoft Word (.doc, .docx)
- Plain text (.txt)
- Rich Text Format (.rtf)

### 10.3 LinkedIn URL Patterns
- `https://www.linkedin.com/jobs/view/{job_id}`
- `https://linkedin.com/jobs/view/{job_id}`
- Support for tracking parameters and mobile URLs