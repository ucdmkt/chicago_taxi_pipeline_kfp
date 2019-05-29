# Self-contained Pipeline Template for Chicago Taxi Pipeline (approach 2)

This repository is based on the '1st approach' to use November DSL with TFX
Components. Trainer and Transform user code will be placed in GCS.

To compile the pipeline, simply do the following.

```shell
# Build child image that embeds pipeline code.
docker build -t ${CHILD_DOCKER_IMAGE_PATH}:${TAG} -f Dockerfile .

# Compile the pipeline.
python -m pipeline.workflow
```
`workflow.tar.gz` is produced under `./pipeline` directory, which you upload to
Kubeflow and run.


To unit-test a component of the pipeline, do the following.

```shell
python -m data_source.example_generator_test
```


## Steps to develop the pipeline.

This template comes with a filly self-contained pipeline to train
a classification model for [Chicago Taxi tip prediction pipeline](https://github.com/tensorflow/tfx/tree/master/tfx/examples/chicago_taxi_pipeline)

1. Update `date_source/example_generator.py` to retried your own training data.
1. Update `pipeline/workflow.py` to add/remove pipeline-level parameters,
   and components, if necessary.
1. Make sure all unit tests pass for components.
1. Make sure integration tests passes (not implemented yet).
1. Compile and run the pipeline in a Kubeflow for experimentation.


## Outstanding development items

*  Not all pipeline-level parameters work. Need to figured out delayed
   evaluation of parameters passed to component at runtime (such as
   `training_steps`).
*  Figure out a way to have `schema.pbtxt` as a pipeline asset.
   * Once figured out, add control flow in the pipeline to execute SchemaGen if
     and only if schema.pbtxt isn't supplied.
*  Bazel and Cloud Build config is not implemented.
*  Integration test is not implemented.
*  Unit test is only a skeleton.
*  Companion notebook.
