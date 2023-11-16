import tensorflow as tf
import os

class Game2048NN(tf.keras.Model):
    def __init__(self):
        super(Game2048NN, self).__init__()
        self.layer1 = tf.keras.layers.Dense(72, activation='relu', input_shape=(18,))
        self.bn1 = tf.keras.layers.BatchNormalization()
        self.layer2 = tf.keras.layers.Dense(288, activation='relu')
        self.bn2 = tf.keras.layers.BatchNormalization()
        self.layer3 = tf.keras.layers.Dense(64, activation='relu')
        self.bn3 = tf.keras.layers.BatchNormalization()
        self.layer4 = tf.keras.layers.Dense(4)

    def call(self, inputs):
        x = self.layer1(inputs)
        x = self.bn1(x)
        x = self.layer2(x)
        x = self.bn2(x)
        x = self.layer3(x)
        x = self.bn3(x)
        x = self.layer4(x)
        return x

def validate_model_architecture(model):
    # Here, you can add code to validate your model's architecture if needed.
    pass

def load_or_create_model():
    model = Game2048NN()
    checkpoint_path = 'game_nn_checkpoint.tf'
    if os.path.exists(checkpoint_path):
        model.load_weights(checkpoint_path)
        print("Model loaded successfully.")
    else:
        print("Checkpoint file not found. Creating a new model.")
        model.save_weights(checkpoint_path)

    return model

# Create an instance of the model and display its summary (optional)
model_instance = Game2048NN()
model_instance.build((None, 18))  # Build the model by specifying the input shape
model_instance.summary()
