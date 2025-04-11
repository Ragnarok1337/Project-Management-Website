# This line specifies the Python 3.8 slim image.
FROM python:3.9-slim
# Copy the current directory contents into the container at /app
WORKDIR /app
# Copy the requirements.txt file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy the application code
COPY . .
# Make port 5000 available to the world outside this container
EXPOSE 5000
# Run the application using Tornado
CMD ["python", "main_app.py"]