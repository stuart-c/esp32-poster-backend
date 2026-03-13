# AGENTS.md (Root Context)

## Environment
You are operating inside a Dockerized devcontainer. Python, Node, Terraform, and Docker-in-Docker are pre-installed. Do not attempt to install global system packages outside of this context.

## System Architecture
This monorepo builds an image management system for Spectra 6 eInk displays.

```mermaid
flowchart LR
    A[Frontend UI] --> B(API Gateway)
    B --> C(API Lambdas)
    C --> D[(DynamoDB)]
    C --> E[SQS]
    E --> F(Image Processing Lambda)
    F --> G[S3/CloudFront]
    G --> H[External Hardware Gateway]
    H -. ESP-NOW .-> I[Displays]
```

- **Frontend UI:** Vue 3 SPA managing image uploads and presentation logic.
- **Backend API & Processing:** API Gateway triggers API Lambda functions that implement the various API calls. These API Lambdas interact with DynamoDB for state changes and send processing jobs to SQS queues. SQS triggers a Python Docker-based Image Processing Lambda to perform heavy image processing (cropping, Spectra 6 dithering, slicing).
- **Device Delivery:** The processed `.bmp`/`.bin` files AND a per-display `manifest.json` are saved to an S3 bucket served by CloudFront. 
- **Hardware Gateway:** An external hardware gateway (which lives outside this repo) polls the CloudFront HTTPS endpoints to download the JSON and cache the images, communicating with the actual displays via low-power ESP-NOW.

## Strict TDD & Human-in-the-loop Workflow
You must strictly follow this sequence and generate Antigravity Artifacts at each review gate:
1. **Plan:** Generate an Implementation Plan Artifact. **[WAIT FOR HUMAN APPROVAL]**
2. **Test:** Write tests (pytest/vitest/terratest) based on the plan. Run them to prove they fail. **[WAIT FOR HUMAN APPROVAL]**
3. **Implement:** Write code to pass tests.
4. **Verify:** Run tests, output logs and diffs. **[WAIT FOR FINAL APPROVAL]**

## ⚠️ Terminal Execution Rule
When executing terminal commands, you **must** append a newline character (`\n` or `↵`) to prevent the terminal from hanging.
