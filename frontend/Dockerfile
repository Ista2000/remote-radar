# Use an official Node.js image
FROM node:18-alpine

# Set the working directory
WORKDIR /app

# Copy environment variables
ARG NEXT_PUBLIC_BACKEND_URL
ENV NEXT_PUBLIC_BACKEND_URL=$NEXT_PUBLIC_BACKEND_URL

# Install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy the application code
COPY . .

# Build the frontend
RUN npm run build

# Expose the frontend port (from .env.local)
EXPOSE 3000

# Start the frontend application
CMD ["npm", "run", "start"]
