"""TensorFlow 2.0 implementation of convolutional variational autoencoder"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

__version__ = '1.0.0'
__author__ = 'Abien Fred Agarap'

import numpy as np
import tensorflow as tf

class Sampling(tf.keras.layers.Layer):
	def call(self, args):
		z_mean, z_log_var = args
		batch = tf.shape(z_mean)[0]
		dim = tf.shape(z_mean)[1]
		epsilon = tf.random.normal(shape=(batch, dim), mean=0., stddev=1.)
		return z_mean + epsilon * tf.exp(0.5 * z_log_var)

	
class Encoder(tf.keras.layers.Layer):
	def __init__(self, latent_dim):
		super(Encoder, self).__init__()
		self.input_layer = tf.keras.layers.InputLayer(input_shape=(28, 28, 1))
		self.conv_layer_1 = tf.keras.layers.Conv2D(filters=32, kernel_size=3, strides=(2, 2), activation=tf.nn.relu)
		self.conv_layer_2 = tf.keras.layers.Conv2D(filters=64, kernel_size=3, strides=(2, 2), activation=tf.nn.relu)
		self.flatten = tf.keras.layers.Flatten()
		self.z_mean_layer = tf.keras.layers.Dense(units=latent_dim)
		self.z_log_var_layer = tf.keras.layers.Dense(units=latent_dim)
		self.sampling = Sampling()
	
	def call(self, input_features):
		input_features = self.input_layer(input_features)
		conv_layer_1_activation = self.conv_layer_1(input_features)
		conv_layer_2_activation = self.conv_layer_2(conv_layer_1_activation)
		flatten_activation = self.flatten(conv_layer_2_activation)
		z_mean = self.z_mean_layer(flatten_activation)
		z_log_var = self.z_log_var_layer(flatten_activation)
		z = self.sampling((z_mean, z_log_var))
		return z_mean, z_log_var, z


class Decoder(tf.keras.layers.Layer):
	def __init__(self, latent_dim):
		super(Decoder, self).__init__()
		self.input_layer = tf.keras.layers.InputLayer(input_shape=(latent_dim, ))
		self.hidden_layer_1 = tf.keras.layers.Dense(units=(7 * 7 * 32), activation=tf.nn.relu)
		self.reshape = tf.keras.layers.Reshape(target_shape=(7, 7, 32))
		self.conv_layer_1 = tf.keras.layers.Conv2DTranpose(filters=64, kernel_size=3, strides=(2, 2), padding='SAME', activation=tf.nn.relu)
		self.conv_layer_2 = tf.keras.layers.Conv2DTranpose(filters=32, kernel_size=3, strides=(2, 2), padding='SAME', activation=tf.nn.relu)
		self.output_layer = tf.keras.layers.Conv2DTranpose(filters=1, kernel_size=3, strides=(1, 1), padding='SAME', activation=tf.nn.sigmoid)

	def call(self, input_features):
		input_features = self.input_layer(input_features)
		activation_1 = self.hidden_layer_1(input_features)
		activation_1 = self.reshape(activation_1)
		conv_layer_1_activation = self.conv_layer_1(activation_1)
		conv_layer_2_activation = self.conv_layer_2(conv_layer_1_activation)
		output = self.output_layer(conv_layer_2_activation)
		return output


class VariationalAutoencoder(tf.keras.Model):
	def __init__(self, latent_dim):
		super(VariationalAutoencoder, self).__init__()
		self.encoder = Encoder(latent_dim=latent_dim)
		self.decoder = Decoder(latent_dim=latent_dim)
	
	def call(self, input_features):
		z_mean, z_log_var, latent_code = self.encoder(input_features)
		reconstructed = self.decoder(latent_code)
		kl_divergence = -5e-2 * tf.reduce_sum(tf.exp(z_log_var) + tf.square(z_mean) - 1 - z_log_var)
		self.add_loss(kl_divergence)
		return reconstructed
