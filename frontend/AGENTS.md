# AGENTS.md (Frontend Context)

## Responsibilities
Manage the Vue 3 SPA for presentation management.

## Technical Stack
- Vue 3 (Composition API), Vite, Vitest.

## Key Features & UI Workflow
- Direct-to-S3 raw image uploads using presigned URLs.
- **Template-Driven Workflow:** 1. The UI must fetch and display available `Layouts` (fixed display grids) from the API.
  2. The user selects an image and overlays it onto the selected `Layout`.
  3. The UI must provide a cropping tool allowing the user to pan/zoom the image to fit the specific aspect ratio of the chosen `Layout`.
- Client-side preview of brightness/contrast adjustments before submitting to the backend API.
