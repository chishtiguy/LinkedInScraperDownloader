# Use the official Apify Python base image
FROM apify/actor-python:3.11

# Copy actor code and dependencies
COPY . ./

# Install Python dependencies
RUN pip install -r requirements.txt

# Run the Python actor
CMD python main.py