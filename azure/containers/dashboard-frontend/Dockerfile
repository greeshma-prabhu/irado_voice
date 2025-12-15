# Irado Dashboard Frontend Container
# Express.js dashboard frontend proxy service

FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache curl

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Copy application code
COPY . .

# Create non-root user
RUN adduser -D -s /bin/sh dashboard-frontend && \
    chown -R dashboard-frontend:dashboard-frontend /app

# Switch to non-root user
USER dashboard-frontend

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3256/health || exit 1

# Expose port
EXPOSE 3256

# Environment variables
ENV NODE_ENV=production
ENV PORT=3256

# Start command
CMD ["node", "dashboard_server.js"]
