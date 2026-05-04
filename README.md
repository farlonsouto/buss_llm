## buss-intelligence-engine

A production-grade Data Engineering pipeline and Intelligence Engine. Compliant with the Medallion structure, it is
designed to transform unstructured public transit feedback (bronze layer) into structured insights (gold layer). It
counts on a local LLM model for inference accelerated on a local Nvidia GPU.

## 🛠 Tech Stack

* Frontend: Streamlit (Python) + Custom CSS/HTML injection.
* Backend: FastAPI (Asynchronous Python 3.10) + Pydantic.
* AI Engine: Ollama (LLM runtime) + Llama 3 (Quantized GGUF).
* Inference: NVIDIA CUDA passthrough (Quadro T2000).
* Infrastructure: Docker Compose (Container Orchestration).

## 🏗 Infrastructure Setup: NVIDIA GPU & Docker

To achieve high-performance inference, this engine requires NVIDIA GPU acceleration.

## 1. Prerequisites

Ensure you have the latest NVIDIA drivers installed on your host. Verify with:
nvidia-smi

## 2. Install NVIDIA Container Toolkit

# Add the package repositories

curl -fsSL https://github.io | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
&& curl -s -L https://github.io | \
sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Install and Configure

sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

## 3. Verification (The Smoke Test)

docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
------------------------------

## 🚀 Getting Started## 1. Deployment

docker compose up --build

Note: The first run will pull ~4.7GB for the LLM. The system includes a healthcheck that waits for the model to be fully
ready.

## 2. Access points

* Web UI: http://localhost:8501
* API Documentation: http://localhost:8000/docs

------------------------------

## 📊 Data Pipeline (Medallion Structure)

* Bronze Layer: Raw unstructured text ingested via the /analyze endpoint.
* Silver Layer: Pydantic-validated models ensuring "Contract-First" data integrity.
* Gold Layer: AI-enriched structured JSON (Sentiment, Category, Priority, Entities).

------------------------------

## 📈 Decision Analysis Resolution (DAR): Scalability & Architecture## The Problem

The current Request-Response architecture is synchronous. Scaling to millions of users would result in VRAM contention,
request timeouts, and catastrophic failure during peak transit hours.

## The Decision: Event-Driven Architecture (EDA)

To scale this engine, the next phase will implement a Broker-Worker pattern using RabbitMQ or Apache Kafka.
Why EDA?

1. Load Leveling: Messages are buffered in a queue; the LLM processes them at its maximum sustainable rate without
   dropping data.
2. Horizontal Scaling: We can spin up multiple worker containers across different GPUs/Nodes to consume the same queue.
3. Resilience: If the LLM service restarts, the "Bronze" data remains safe in the message broker.

## Literature & References

* Designing Data-Intensive Applications (Martin Kleppmann): Implementation of "Consumer Groups" and partition-based
  scaling.
* Building Microservices (Sam Newman): Use of asynchronous messaging to prevent "Distributed Monolith" bottlenecks.
* Enterprise Integration Patterns (Gregor Hohpe): Utilizing the "Message Dispatcher" pattern to distribute LLM workloads
  across a heterogeneous GPU cluster.

------------------------------

## 🛡 Engineering Standards

* Contract-First: Backend and Frontend share Pydantic/JSON schemas.
* Resource Management: Explicit GPU reservations and health-checks.
* Observability: Structured logging for tracking LLM inference latency.
