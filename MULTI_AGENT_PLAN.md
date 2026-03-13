# Parallel Multi-Agent Implementation Plan

## Goal Description
Establish a system for multiple agents to design, build, and document the ESP32 Poster Management system in strictly parallel tracks. This plan covers the initial design phase, safe Git worktree isolation, TDD workflows, CI/CD GitHub Actions setup, and documentation requirements.

## Proposed Parallel Tracks

To avoid merge conflicts and race conditions, work will be divided into the following 5 independent tracks. Each agent will operate in its own git worktree (`.trees/agent-<track-name>`) and adhere to the strict TDD workflow.

### Track 1: Infrastructure & CI/CD
**Focus:** GitHub Actions workflows and Terraform infrastructure.
- **Tasks:**
  - Create `.github/workflows/pr-build-test.yml` to run tests (`pytest`, `vitest`, `terratest`) on Pull Requests.
  - Create `.github/workflows/deploy-main.yml` to apply Terraform and trigger deployments automatically on `main` branch merges.
  - Scaffold base Terraform resources (DynamoDB table, SQS queue, S3 bucket structure, CloudFront distribution).

### Track 2: Backend API & Storage
**Focus:** Core REST API and DynamoDB state management.
- **Tasks:**
  - Define API Gateway endpoints, schemas, and DynamoDB access patterns.
  - Test and implement API Lambdas (file upload initiation, status checking, manifest delivery).
  - Implement publishing of image processing jobs to SQS.

### Track 3: Image Processing Pipeline
**Focus:** The computational heavy-lifting container.
- **Tasks:**
  - Create test fixtures for the image processing Python Docker Lambda.
  - Implement algorithms: scaling, cropping, Spectra 6 dithering, and slicing into `.bmp`/`.bin` files.
  - Wire SQS consumption, DynamoDB status updates, and S3 artifact uploading.

### Track 4: Frontend UI
**Focus:** The Vue 3 Single Page Application.
- **Tasks:**
  - Scaffold UI framework and write component tests for the Vue 3 SPA.
  - Implement visual components for image submission, task monitoring, and display management.
  - Integrate with the Backend APIs.

### Track 5: Documentation
**Focus:** Project documentation and specifications.
- **Tasks:**
  - Document the overarching system architecture map and component interaction.
  - Keep `README.md` and developer setup guides descriptive and current.
  - Explicitly document the JSON manifest schema expected by the external ESP-NOW hardware gateway.

## Workflow Rules & Git Worktree Usage
* **Root Isolation:** All auxiliary worktrees must be created within the `.trees/` directory at the project root.
* **Pathing:** The standard format for a worktree path is `.trees/agent-{track-id}`.
* **TDD Loop:** Plan -> Test -> Implement -> Verify -> Wait for Manager Approval.
