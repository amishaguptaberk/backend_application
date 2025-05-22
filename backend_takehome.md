

## Project Overview



Build a simple URL shortener service that provides RESTful API endpoints for creating and accessing shortened URLs. You'll also containerize the application, set up CI/CD pipelines, and deploy the service to Google Cloud.



---



## Requirements



### Part 1: Creating the Service



Create a RESTful API with the following endpoints:



- `POST /shorten`  

  Accepts a long URL and returns a short code and shortened URL.



- `GET /{short_code}`  

  Redirects to the original long URL.



- `GET /analytics/{short_code}`  

  Returns basic statistics: number of redirects, timestamp of creation, etc.



#### Implementation Requirements:

- Use any language/framework you are comfortable with, but Python and Django are preferred.

- Store data using a lightweight database (e.g., **MySQL**, **PostgreSQL**)

- Include **basic unit tests** for core logic

- Handle edge cases (invalid URLs, missing codes, etc.)



---



### Part 2: Containerization



- Write a `Dockerfile` for the backend service

- Ensure the service is accessible when running the container



---



### Part 3: CI/CD Pipeline



- Use **GitHub Actions** to:

  - Run linters

  - Execute unit tests

  - Build and push the Docker image to a container registry (e.g., Docker Hub or GitHub Container Registry)



---



### Part 4: Infrastructure



#### Deployment Target:



- **Google Cloud Run**

  - Deploy your Dockerized service to Cloud Run

  - Configure environment variables, concurrency, and timeouts



#### IAM & Security:

- Use **GCP IAM roles** to scope access (e.g., allow your service account to access Cloud SQL)

- Ensure **service-to-service authentication** where applicable



#### Optional Extras:

- Provision and connect to **Cloud SQL** (PostgreSQL or MySQL)

- Use **Secret Manager** for managing API keys or DB credentials

- Configure **Cloud Logging** and **Cloud Monitoring**

- Set up alerts or uptime checks

- Create integration tests that verify the service's functionality



---



### Part 5: Real-Time Analytics (WebSocket Extension) _(Optional)_



To demonstrate your ability to handle real-time communication, extend the service with **WebSocket support** to provide live analytics updates.



#### Task Description:

- Implement a WebSocket endpoint (e.g., `/ws/analytics/{short_code}`).

- When a client connects to this endpoint, they should receive **real-time updates** on the number of redirects for the given `short_code`.

- Whenever the `GET /{short_code}` redirect endpoint is triggered, the server should push the updated analytics data (e.g., incremented redirect count) to any connected WebSocket clients watching that `short_code`.



#### Requirements:

- Handle multiple concurrent WebSocket connections gracefully.

- Include basic unit/integration tests for this functionality.

- Ensure clients that disconnect are cleaned up properly.

- Optionally, support sending a heartbeat/ping message every N seconds to keep connections alive.



#### Bonus Points:

- Add authentication to the WebSocket endpoint.

- Support subscribing to **multiple short codes** in a single connection (e.g., by sending a JSON message to select short codes after connecting).

- Add a small client-side example (could be a simple CLI script or HTML page) demonstrating subscribing to these WebSocket updates.



---



## Submission Instructions



- Push your code to a **public GitHub repository**

- Include the following in your `README.md`:

  - How to run the project locally

  - Example curl commands or Postman/Bruno collection for using the API

  - How the CI/CD works

  - How deployment works

  - Time breakdown (roughly how long you spent on each part)

  - Any tradeoffs or shortcuts you made



---



## Evaluation Criteria



- Correctness and functionality

- Code quality and structure

- Clarity of documentation

- CI/CD workflow

- Docker and infrastructure usage

- Bonus: Monitoring/logging tools, metrics, or alerts



---



## Tips



- Don’t over-engineer — keep things simple and functional

- Make reasonable assumptions and document them

- You’re encouraged to Google, AI models, and use open-source libraries (but please cite them!)

- Treat this like a small project you'd ship at work



---



Good luck! 🚀



