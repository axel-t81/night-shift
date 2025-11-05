# Use an official Python runtime as a parent image
FROM python:3.11-slim
        
# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code
COPY . .

# Expose the port the app runs on
EXPOSE 8080

# Run the application with Gunicorn
# Use shell form to expand the PORT environment variable
CMD ["sh", "-c", "sleep 5 && gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8080"]