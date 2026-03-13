FROM public.ecr.aws/lambda/python:3.12

# Install uv for fast dependency resolution
RUN pip install uv

# Copy uv dependency file
COPY pyproject.toml .

# export requirements from uv to standard pip format
RUN uv pip compile pyproject.toml -o requirements.txt

# Install dependencies using standard pip for a lambda environment
RUN pip install -r requirements.txt -t .

# Copy function code
COPY src/ ${LAMBDA_TASK_ROOT}/src/

# Set the CMD to your handler
CMD [ "src.main.handler" ]
