FROM python:3.11-slim

LABEL maintainer="lvbibir"
LABEL description="JetBrainsLxgwNerdMono Font Builder"

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml uv.lock README.md config.yaml ./
COPY src/ src/
COPY build.py .

# Install dependencies
RUN uv sync --locked --no-dev

# Create mount points
VOLUME /app/fonts
VOLUME /app/output

# Default entrypoint
ENTRYPOINT ["uv", "run", "--no-sync", "python", "build.py", "--fonts-dir", "/app/fonts", "--output-dir", "/app/output/fonts"]

# Default command (can be overridden)
CMD []
