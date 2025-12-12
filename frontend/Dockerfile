# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY frontend/ ./

# Build arguments for environment variables
# Cloud Build uses _ prefix for substitutions, so handle both cases
ARG _VITE_API_BASE_URL
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${_VITE_API_BASE_URL:-${VITE_API_BASE_URL}}

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

