# Copyright 2019 ZTE corporation. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os
from tempfile import TemporaryDirectory
from unittest import TestCase

import tensorflow as tf

import model_compiler.compilers.tf_model_file_to_openvino_model as compiler
from model_compiler.compilers.tf_model_file_to_openvino_model import Config
from model_compiler.models.sources.tf_model_file import TfModelFile
from model_compiler.protos.generated.model_config_pb2 import ModelInput, ModelOutput


class ConfigTestCase(TestCase):
    def test_from_json_all_names(self):
        self.assertEqual(Config.from_json({'input_names': ['input'],
                                           'input_shapes': [[1, 2, 3, 4]],
                                           'output_names': ['output'],
                                           'max_batch_size': 1,
                                           'enable_nhwc_to_nchw': False}),
                         Config(input_names=['input'],
                                input_shapes=[[1, 2, 3, 4]],
                                output_names=['output'],
                                max_batch_size=1,
                                enable_nhwc_to_nchw=False))

    def test_from_json_no_names(self):
        self.assertEqual(Config.from_json({}),
                         Config())

    def test_from_env_all_names(self):
        self.assertEqual(Config.from_env({'INPUT_NAMES': 'input',
                                          'INPUT_SHAPES': '[1, 2, 3, 4]',
                                          'OUTPUT_NAMES': 'output',
                                          'MAX_BATCH_SIZE': '1',
                                          'ENABLE_NHWC_TO_NCHW': '0'}),
                         Config(input_names=['input'],
                                input_shapes=[[1, 2, 3, 4]],
                                output_names=['output'],
                                max_batch_size=1,
                                enable_nhwc_to_nchw=False))

    def test_from_env_no_names(self):
        self.assertEqual(Config.from_env({}),
                         Config())


def _save_tensorflow_model(model_path):
    with tf.compat.v1.Session(graph=tf.Graph()) as session:
        input_x = tf.compat.v1.placeholder(dtype=tf.float32, shape=[None, 2, 3, 4], name='x')
        input_y = tf.compat.v1.placeholder(dtype=tf.float32, shape=[None, 2, 3, 4], name='y')
        weight = tf.Variable(initial_value=4.2, dtype=tf.float32)
        tf.multiply(input_x + input_y, weight, name='z')

        session.run(weight.initializer)

        tf.compat.v1.train.Saver().save(session, model_path)


class CompileSourceTestCase(TestCase):
    def test_compile_with_no_params(self):
        with TemporaryDirectory() as directory:
            model_path = os.path.join(directory, 'model.ckpt')
            _save_tensorflow_model(model_path)
            config = Config.from_json({'max_batch_size': 1})
            compiled = compiler.compile_source(TfModelFile(model_path=model_path), config)
            self.assertEqual(compiled.get_inputs(),
                             [ModelInput(name='x', data_type=tf.float32.as_datatype_enum,
                                         format=ModelInput.FORMAT_NONE, dims=[2, 3, 4]),  # pylint: disable=no-member
                              ModelInput(name='y', data_type=tf.float32.as_datatype_enum,
                                         format=ModelInput.FORMAT_NONE, dims=[2, 3, 4])])  # pylint: disable=no-member
            self.assertEqual(compiled.get_outputs(),
                             [ModelOutput(name='z', data_type=tf.float32.as_datatype_enum, dims=[2, 3, 4])])

    def test_compile_with_fp16(self):
        with TemporaryDirectory() as directory:
            model_path = os.path.join(directory, 'model.ckpt')
            _save_tensorflow_model(model_path)
            config = Config.from_json({'max_batch_size': 1,
                                       'data_type': 'FP16'})
            compiled = compiler.compile_source(TfModelFile(model_path=model_path), config)
            self.assertEqual(compiled.get_inputs(),
                             [ModelInput(name='x', data_type=tf.float16.as_datatype_enum,
                                         format=ModelInput.FORMAT_NONE, dims=[2, 3, 4]),  # pylint: disable=no-member
                              ModelInput(name='y', data_type=tf.float16.as_datatype_enum,
                                         format=ModelInput.FORMAT_NONE, dims=[2, 3, 4])])  # pylint: disable=no-member
            self.assertEqual(compiled.get_outputs(),
                             [ModelOutput(name='z', data_type=tf.float16.as_datatype_enum, dims=[2, 3, 4])])

    def test_compile_with_all_params_with_batch_size(self):
        with TemporaryDirectory() as directory:
            model_path = os.path.join(directory, 'model.ckpt')
            _save_tensorflow_model(model_path)
            config = Config.from_json({'input_names': ['x', 'y'],
                                       'output_names': ['z'],
                                       'enable_nhwc_to_nchw': False,
                                       'max_batch_size': 1})
            compiled = compiler.compile_source(TfModelFile(model_path=model_path), config)
            self.assertEqual(compiled.get_inputs(),
                             [ModelInput(name='x', data_type=tf.float32.as_datatype_enum,
                                         format=ModelInput.FORMAT_NONE, dims=[2, 3, 4]),  # pylint: disable=no-member
                              ModelInput(name='y', data_type=tf.float32.as_datatype_enum,
                                         format=ModelInput.FORMAT_NONE, dims=[2, 3, 4])])  # pylint: disable=no-member
            self.assertEqual(compiled.get_outputs(),
                             [ModelOutput(name='z', data_type=tf.float32.as_datatype_enum, dims=[2, 3, 4])])

    def test_compile_with_all_params_with_shape(self):
        with TemporaryDirectory() as directory:
            model_path = os.path.join(directory, 'model.ckpt')
            _save_tensorflow_model(model_path)
            config = Config.from_json({'input_names': ['x', 'y'],
                                       'input_shapes': [[1, 2, 3, 4], [1, 2, 3, 4]],
                                       'output_names': ['z'],
                                       'enable_nhwc_to_nchw': False})
            compiled = compiler.compile_source(TfModelFile(model_path=model_path), config)
            self.assertEqual(compiled.get_inputs(),
                             [ModelInput(name='x', data_type=tf.float32.as_datatype_enum,
                                         format=ModelInput.FORMAT_NONE, dims=[2, 3, 4]),  # pylint: disable=no-member
                              ModelInput(name='y', data_type=tf.float32.as_datatype_enum,
                                         format=ModelInput.FORMAT_NONE, dims=[2, 3, 4])])  # pylint: disable=no-member
            self.assertEqual(compiled.get_outputs(),
                             [ModelOutput(name='z', data_type=tf.float32.as_datatype_enum, dims=[2, 3, 4])])

    def test_compile_with_all_params_with_enable_nhwc_to_nchw_true(self):
        with TemporaryDirectory() as directory:
            model_path = os.path.join(directory, 'model.ckpt')
            _save_tensorflow_model(model_path)
            config = Config.from_json({'input_names': ['x', 'y'],
                                       'output_names': ['z'],
                                       'enable_nhwc_to_nchw': True,
                                       'max_batch_size': 1})
            compiled = compiler.compile_source(TfModelFile(model_path=model_path), config)
            self.assertEqual(compiled.get_inputs(),
                             [ModelInput(name='x', data_type=tf.float32.as_datatype_enum,
                                         format=ModelInput.FORMAT_NONE, dims=[4, 2, 3]),  # pylint: disable=no-member
                              ModelInput(name='y', data_type=tf.float32.as_datatype_enum,
                                         format=ModelInput.FORMAT_NONE, dims=[4, 2, 3])])  # pylint: disable=no-member
            self.assertEqual(compiled.get_outputs(),
                             [ModelOutput(name='z', data_type=tf.float32.as_datatype_enum, dims=[4, 2, 3])])
