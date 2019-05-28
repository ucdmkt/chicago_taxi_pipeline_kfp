FROM tensorflow/tfx:0.13.0

RUN apt-get update -y && apt-get install -y python3
#COPY ../../tfx_component_runner.py /bin/tfx_component_runner.py

# Copy all pipeline user code into the image
COPY . /srcs/

#ENTRYPOINT ["python", "/bin/tfx_component_runner.py"]
