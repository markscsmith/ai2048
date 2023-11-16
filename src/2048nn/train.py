import tensorflow as tf


def train_model(model, training_states, training_moves):
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
      # Restrict TensorFlow to only use the first GPU
        try:
            tf.config.set_visible_devices(gpus[0], 'GPU')
            logical_gpus = tf.config.list_logical_devices('GPU')
            print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPU")
        except RuntimeError as error:
        # Visible devices must be set before GPUs have been initialized
            print(error)
    if len(training_states) <= 1:
        print("Batch size is too small for batch normalization. Skipping this batch.")
        return

    criterion = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
    optimizer = tf.keras.optimizers.legacy.Adam(learning_rate=0.05)

    with tf.GradientTape() as tape:
        outputs = model(training_states)
        loss = criterion(training_moves, outputs)

    grads = tape.gradient(loss, model.trainable_variables)
    with tf.device("/GPU:0"):
        optimizer.apply_gradients(zip(grads, model.trainable_variables))

    print(f"Loss: {loss}")
