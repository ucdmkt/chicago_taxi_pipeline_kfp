#FROM tensorflow/tfx:0.13.0
FROM gcr.io/caipe-dev/tensorflow/tfx-muchida:latest

RUN apt-get update -y && apt-get install -y python3
#COPY ../../tfx_component_runner.py /bin/tfx_component_runner.py

# Copy all pipeline user code into the image.
# This is the atomic unit of continuous integration of pipeline user code.
# Pipeline continuous delivery is managed by combination of
# (image sha, git commit hash of pipeline/workflow.tar.gz)
COPY . /pipeline-srcs/
