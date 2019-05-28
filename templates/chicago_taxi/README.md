# Self-contained Pipeline Template for Chicago Taxi Pipeline

This repository is based on the '1st approach' to use November DSL with TFX
Components. Trainer and Transform user code will be placed in GCS.


To compile the pipeline, simply do the following.

```shell
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
2. Update `model_training/taxi_util.py` to according to your data and modeling
   objective, and upload it to a GCS location.
3. Update `pipeline/workflow.py` to add/remove pipeline-level parameters,
   and components, if necessary.
4. Make sure all unit tests pass for components.
5. Make sure integration tests passes (not implemented yet).
6. Compile and run the pipeline in a Kubeflow for experimentation.

