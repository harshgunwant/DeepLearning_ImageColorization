# DeepLearning_ImageColorization


This repository contains an implementation of deep learning-based image colorization using Tesnorflow. The project aims to automatically add colors to grayscale images using a convolutional neural network (CNN).--EFFICIENTNET-B0

## Dependencies

To run the code in this repository, you need the following dependencies:

- Python (3.6 or higher)
- Tensorflow
- NumPy
- Matplotlib


## Dataset

The project uses a dataset of grayscale images paired with their corresponding color images for training. The dataset is not included in this repository, but you can provide your own dataset in the required format. Each grayscale image should have its corresponding color image with the same filename.

## Usage

To train the colorization model, you can run the `HarshCode.py` script. Before running the script, make sure to set the appropriate parameters, such as the paths to the dataset and the desired hyperparameters.

To colorize a grayscale image using the trained model, you can use the `HarshCode.py` script. Provide the path to the grayscale image as a command-line argument.



## Model Architecture

The colorization model follows an encoder-decoder architecture. It consists of an encoder network that extracts high-level features from the input grayscale image, followed by a decoder network that generates the colorized output. The specific architecture details and hyperparameters can be found in the code.

## Results

The repository includes sample results of colorized images obtained from the trained model. You can find these results in the `results` folder.

## Contributing

Contributions to this project are welcome. You can open issues for bug reports or feature requests. If you would like to contribute code, please fork the repository and create a pull request with your changes.

## License

The code in this repository is available under the [MIT License](LICENSE).



