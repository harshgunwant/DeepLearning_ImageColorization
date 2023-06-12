# -*- coding: utf-8 -*-
"""HarshCode.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1tDmxT7Z6DvNlEOEvb08nCKIFCLZ0mbWE
"""

!pip install efficientnet

import tensorflow as tf
from tensorflow.keras.applications.efficientnet import EfficientNetB0
from tensorflow.keras.preprocessing import image
from tensorflow.keras.layers import Conv2D, UpSampling2D, InputLayer, Conv2DTranspose, Input, Reshape, concatenate
from tensorflow.keras.layers import Activation, Dense, Dropout, Flatten
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.applications.inception_resnet_v2 import preprocess_input
from tensorflow.keras.callbacks import TensorBoard, ModelCheckpoint
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import RepeatVector
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from PIL import Image
import numpy as np
import os
from skimage.color import rgb2lab, lab2rgb, rgb2gray, gray2rgb
from skimage.transform import resize
from skimage.io import imsave

# Set GPU device
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

# GPU memory growth
physical_devices = tf.config.list_physical_devices("GPU")
print(physical_devices)
tf.config.experimental.set_memory_growth(physical_devices[0], True)
# Check if GPU is available
if physical_devices:
    print("GPU is available. Running on GPU.")
else:
    print("GPU is not available. Running on CPU.")

def array_to_img(x, data_format=None, scale=True, dtype=None):
    if scale:
        x = x.clip(0, 255)
    x = x.astype('uint8')
    return Image.fromarray(x, mode='RGB')

def load_img(path, grayscale=False, color_mode='rgb', target_size=None, interpolation='nearest'):
    return Image.open(path)

def img_to_array(img, data_format=None, dtype=None):
    if data_format is None:
        data_format = 'channels_last'
    if dtype is None:
        dtype = np.float32

    x = np.asarray(img, dtype=dtype)

    if data_format == 'channels_first':
        x = x.transpose(2, 0, 1)

    return x

# Get images
X = []
image_dir = 'true_images/'
num_images = 100  # Number of images to load
target_image_size = (256, 256)

for i, filename in enumerate(os.listdir(image_dir)):
    if i >= num_images:
        break
    img = load_img(os.path.join(image_dir, filename))
    img = img.resize(target_image_size)  # Resize image
    X.append(img_to_array(img))
X = np.array(X, dtype=float)
Xtrain = 1.0 / 255 * X

# Load weights
effnet = EfficientNetB0(weights='imagenet', include_top=False, pooling='avg')

embed_input = Input(shape=(1280,))

# Encoder
encoder_input = Input(shape=(256, 256, 1,))
encoder_output = Conv2D(64, (3, 3), activation='relu', padding='same', strides=2)(encoder_input)
encoder_output = Conv2D(128, (3, 3), activation='relu', padding='same')(encoder_output)
encoder_output = Conv2D(128, (3, 3), activation='relu', padding='same', strides=2)(encoder_output)
encoder_output = Conv2D(256, (3, 3), activation='relu', padding='same')(encoder_output)
encoder_output = Conv2D(256, (3, 3), activation='relu', padding='same', strides=2)(encoder_output)
encoder_output = Conv2D(512, (3, 3), activation='relu', padding='same')(encoder_output)
encoder_output = Conv2D(512, (3, 3), activation='relu', padding='same')(encoder_output)
encoder_output = Conv2D(256, (3, 3), activation='relu', padding='same')(encoder_output)

# Fusion
fusion_output = RepeatVector(32 * 32)(embed_input)
fusion_output = Reshape(([32, 32, 1280]))(fusion_output)
fusion_output = concatenate([encoder_output, fusion_output], axis=3)
fusion_output = Conv2D(256, (1, 1), activation='relu', padding='same')(fusion_output)

# Decoder
decoder_output = Conv2D(128, (3, 3), activation='relu', padding='same')(fusion_output)
decoder_output = UpSampling2D((2, 2))(decoder_output)
decoder_output = Conv2D(64, (3, 3), activation='relu', padding='same')(decoder_output)
decoder_output = UpSampling2D((2, 2))(decoder_output)
decoder_output = Conv2D(32, (3, 3), activation='relu', padding='same')(decoder_output)
decoder_output = Conv2D(16, (3, 3), activation='relu', padding='same')(decoder_output)
decoder_output = Conv2D(2, (3, 3), activation='tanh', padding='same')(decoder_output)
decoder_output = UpSampling2D((2, 2))(decoder_output)

model = Model(inputs=[encoder_input, embed_input], outputs=decoder_output)

def create_effnet_embedding(grayscaled_rgb):
    grayscaled_rgb_resized = []
    for i in grayscaled_rgb:
        i = resize(i, (299, 299, 3), mode='constant')
        grayscaled_rgb_resized.append(i)
    grayscaled_rgb_resized = np.array(grayscaled_rgb_resized)
    grayscaled_rgb_resized = preprocess_input(grayscaled_rgb_resized)
    embed = effnet.predict(grayscaled_rgb_resized)
    return embed

# Image transformer
datagen = ImageDataGenerator(
    shear_range=0.2,
    zoom_range=0.2,
    rotation_range=20,
    horizontal_flip=True)

# Generate training data
batch_size = 10

def image_a_b_gen(batch_size):
    for batch in datagen.flow(Xtrain, batch_size=batch_size):
        grayscaled_rgb = gray2rgb(rgb2gray(batch))
        embed = create_effnet_embedding(grayscaled_rgb)
        lab_batch = rgb2lab(batch)
        X_batch = lab_batch[:, :, :, 0]
        X_batch = X_batch.reshape(X_batch.shape + (1,))
        Y_batch = lab_batch[:, :, :, 1:] / 128
        yield ([X_batch, create_effnet_embedding(grayscaled_rgb)], Y_batch)

# Define the checkpoint callback
checkpoint = ModelCheckpoint("HFinal1/model_weights_H{epoch:02d}.h5", save_weights_only=True, period=10)

# Train model
model.compile(optimizer='rmsprop', loss='mse')
model.fit(image_a_b_gen(batch_size), epochs=500, steps_per_epoch=10, callbacks=[checkpoint])

# Load black-and-white images
bw_images_dir = 'bw_images/'
color_me = []
num_images = 8  # Limit the number of images to load

for filename in os.listdir(bw_images_dir)[:num_images]:
    img = Image.open(os.path.join(bw_images_dir, filename))
    img = img.resize((256, 256))  # Resize image to target size
    color_me.append(np.array(img))

color_me = np.array(color_me, dtype=float)
color_me = color_me / 255.0  # Normalize to the range [0, 1]

# Convert grayscale images to RGB
color_me_rgb = np.stack((color_me,) * 3, axis=-1)

# Convert RGB images to LAB color space
color_me_lab = rgb2lab(color_me_rgb)

# Separate L, AB channels
color_me_l = color_me_lab[:, :, :, 0]
color_me_ab = color_me_lab[:, :, :, 1:]

# Reshape L channel for model input
color_me_l = color_me_l.reshape(color_me_l.shape + (1,))

# Generate output
color_me_embed = create_effnet_embedding(color_me_rgb[:num_images])  # Limit to the same number of images

# # Load the trained weights
model.load_weights("HFinal1/model_weights_H500.h5")

# Predict colorized images
output = model.predict([color_me_l, color_me_embed[:num_images]])
output = output * 128.0

# Merge L channel with predicted AB channels
colorized_images_lab = np.concatenate([color_me_l, output], axis=3)

# Convert LAB images to RGB
colorized_images_rgb = lab2rgb(colorized_images_lab)

# Convert floating-point values to the range [0, 255] and change data type to uint8
colorized_images_rgb = (colorized_images_rgb * 255.0).astype(np.uint8)

# Save colorized images
output_dir = 'Hars/'
for i in range(len(colorized_images_rgb)):
    imsave(output_dir + "result_%d.png" % (i + 1), colorized_images_rgb[i])

