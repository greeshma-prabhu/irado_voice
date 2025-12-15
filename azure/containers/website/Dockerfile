# Irado Website Container
# Express.js website proxy service

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
RUN adduser -D -s /bin/sh website && \
    chown -R website:website /app

# Switch to non-root user
USER website

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3254/health || exit 1

# Expose port
EXPOSE 3254

# Environment variables
ENV NODE_ENV=production
ENV PORT=3254

# Start command
CMD ["node", "express_server.js"]
