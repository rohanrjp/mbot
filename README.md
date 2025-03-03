
# Mbot – A GitHub PR Code Reviewer

Mbot is an AI-powered GitHub PR reviewer built with FastAPI. It leverages Gemini 1.5 Pro to analyze pull requests and provide smart suggestions for code improvements.


## Features

- **Automated GitHub PR Code Review** → Uses GitHub Webhooks to trigger automated code reviews for pull requests, analyzing changes and providing insights. 
- **Built with FastAPI ,Uvicorn & uv** → High-performance backend leveraging FastAPI for speed, Uvicorn as the ASGI server, and uv for dependency management.
- **Secure GitHub Authorization** → Authenticates using a GitHub App with secure API access via private keys.
- **Dockerized for Easy Deployment** → Containerized with Docker, ensuring portability and seamless deployment across environments.
- **CI/CD with GitHub Actions** → Automates building and pushing the latest Docker image to Docker Hub on every push to the main branch.
- **Seamless Deployment on Google Cloud Run** → Google Cloud Run automatically pulls the latest Docker image and deploys updates with zero downtime.


## Installation

Clone the repository

```bash
  git clone https://github.com/rohanrjp/MBot.git
```
Run Locally with Docker

```bash
docker build -t mbot .
docker run -p 8080:8080 mbot
```

## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`GEMINI_API_KEY` -> API key for accessing Gemini AI to analyze and review code changes.

`GITHUB_APP_ID` -> The GitHub App ID used to authenticate as a GitHub App for PR review.

`GITHUB_PRIVATE_KEY` -> Private key for securely signing GitHub API requests as the app.

## API Reference

#### Root endpoint

```http
  GET /
```

#### Get Github webhook requests and post PR code review comments

```http
  POST /api/pr_review
```



## Tech Stack

**Backend:** FastAPI , Uvicorn \
**Deployment:** Docker , Google Cloud Run , GitHub Actions \
**Development Tools:** Ngrok , Httpx 


## Lessons Learned

## What I learnt while building this project?  

Building **MBot** provided valuable insights into **GitHub webhooks**, **authorization**, and **automated CI/CD workflows**. I deepened my understanding of **FastAPI**, **uvicorn**, and **uv**, optimizing API performance and request handling. Deploying the project using **Docker** and **Google Cloud Run** helped reinforce best practices for containerization and cloud deployment.  

## What challenges did you face, and how did you overcome them?  

### 1. Webhook Handling & Authorization  
Setting up GitHub webhooks and managing authentication with **GitHub App ID and private keys** required a precise configuration. I overcame this by thoroughly reading GitHub’s documentation and debugging using **Ngrok** to test webhook events locally.  

### 2. Docker & Cloud Deployment Issues  
Initially, I faced issues with exposed ports and Google Cloud Run failing to detect the correct service port. Fixing this required explicitly setting the `PORT` environment variable and ensuring that FastAPI was listening on `0.0.0.0:8080`.  

### 3. CI/CD Automation  
Automating Docker image builds and deployments with **GitHub Actions** had some challenges with authentication (Docker Hub & Google Cloud). Using **GitHub Secrets** for secure credential management and refining the workflow YAML helped in streamlining deployments.  

Each challenge strengthened my understanding of cloud-based API deployment, containerized applications, and CI/CD automation. 


## Screenshots

![Screenshots](https://imgur.com/H357tWL)
![Screenshots](https://imgur.com/E3GYteA)


## Roadmap

- Implement a feature that **detects which lines of code were modified**  
- Expand AI capabilities to detect **security vulnerabilities** in PRs 
- Explore **fine-tuning a custom model** for even better PR insights





## Authors

- [@rohanrjp](https://github.com/rohanrjp)


## Feedback

If you have any feedback, please reach out to us at rohan1007rjp@gmail.com

