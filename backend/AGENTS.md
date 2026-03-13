# AGENTS.md (Backend Context)

## Responsibilities
Manage the Python backend: API Gateway, DynamoDB, SQS, and the Image Processing Lambda.

## Local Development
- Use `docker-compose.yml` to spin up LocalStack for testing.

## API Framework Selection
- An early design task for an agent should be to scope framework options (e.g., FastAPI vs Flask vs raw Lambda handlers) and present pros & cons to the user for agreement.

## Database Strategy
- **Layouts vs. Presentations:** You must separate physical display layouts from content presentations into 2 separate tables.
- A `Layout` document defines the physical grid (Display IDs, resolutions, X/Y offsets).
- A `Presentation` document links a Raw Image to a `Layout` ID and stores user adjustments/crops.
- The precise design of the schema should be an early task for an agent to design.

## The Image Processing Lambda
- Must be a Docker Container Image for ECR deployment.
- **Input:** Triggered by SQS with the `Presentation` document payload.
- **Logic:** 1. Fetch the raw image from S3.
  2. Fetch the referenced `Layout` document from DynamoDB to get the grid math.
  3. Apply the user's base crop and adjustments.
  4. Iterate over the Layout's `Displays` array to slice the image according to the X/Y offsets.
  5. Apply Spectra 6 dithering to each slice.
- **Output:** Write the processed `.bmp`/`.bin` files and a `manifest.json` for each target display to the CloudFront-backed S3 bucket.
