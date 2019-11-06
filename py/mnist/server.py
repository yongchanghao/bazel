import os
import sys

import tensorflow as tf
from matplotlib import pyplot as plt
from tensorflow import keras
from tornado import web, websocket, ioloop, options

OUTPUT_SIZE = 10
EPOCHS = 3
BATCH_SIZE = 32

rel_path = os.path.abspath(sys.path[0])


def get_image_tensor_from_base64(base64_string):
    base64_string = base64_string.replace('/', '_')
    base64_string = base64_string.replace('+', '-')
    img_tensor = tf.io.decode_base64(base64_string)
    img_tensor = tf.image.decode_image(img_tensor)
    img_tensor = tf.image.rgb_to_grayscale(img_tensor)
    img_tensor = tf.reshape(img_tensor, (img_tensor.shape[0], img_tensor.shape[1]))
    img_tensor = tf.expand_dims(img_tensor, 0)
    img_tensor = tf.expand_dims(img_tensor, 3)
    return img_tensor


def predict(img_tensor):
    model = keras.models.load_model(os.path.join(rel_path, "model.hdf5"))
    return int(tf.argmax(model.predict(img_tensor)[0]))


def train():
    (train_x, train_y), (validation_x, validation_y) = keras.datasets.mnist.load_data()
    train_x = tf.expand_dims(train_x, 3)
    validation_x = tf.expand_dims(validation_x, 3)

    model = keras.models.Sequential([
        keras.layers.Conv2D(64, 3, padding="same", input_shape=(28, 28, 1), activation="relu"),
        keras.layers.MaxPooling2D(),
        keras.layers.Conv2D(32, 3, padding="same", activation="relu"),
        keras.layers.MaxPooling2D(),
        keras.layers.Conv2D(16, 3, padding="same", activation="relu"),
        keras.layers.MaxPooling2D(),
        keras.layers.Flatten(),
        keras.layers.Dense(OUTPUT_SIZE),
        keras.layers.Softmax(),
    ])

    checkpointer = keras.callbacks.ModelCheckpoint(filepath=os.path.join(rel_path, "model.hdf5"), verbose=1,
                                                   save_best_only=True)
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])

    train_image_generator = keras.preprocessing.image.ImageDataGenerator(rescale=1.0 / 255)
    validation_image_generator = keras.preprocessing.image.ImageDataGenerator(rescale=1.0 / 255)
    train_data_gen = train_image_generator.flow(train_x, train_y, batch_size=BATCH_SIZE)
    validation_data_gen = validation_image_generator.flow(validation_x, validation_y, batch_size=BATCH_SIZE)
    history = model.fit_generator(
        train_data_gen,
        steps_per_epoch=len(train_x) // BATCH_SIZE,
        epochs=EPOCHS,
        validation_data=validation_data_gen,
        validation_steps=len(validation_x) // BATCH_SIZE,
        callbacks=[checkpointer]
    )

    acc = history.history['accuracy']
    loss = history.history['loss']

    epochs_range = range(EPOCHS)

    plt.figure(figsize=(8, 8))
    plt.subplot(1, 2, 1)
    plt.plot(epochs_range, acc, label='Training Accuracy')
    plt.legend(loc='lower right')
    plt.title('Training Accuracy')
    plt.subplot(1, 2, 2)
    plt.plot(epochs_range, loss, label='Training Loss')
    plt.legend(loc='upper right')
    plt.title('Training Loss')
    plt.show()


class MainHandler(web.RequestHandler):
    def get(self):
        self.render(template_name="index.html",
                    server_address=options.options.server_address,
                    server_port=options.options.server_port,
                    server_routing=options.options.server_prefix + "/ws")


class DrawingHandler(websocket.WebSocketHandler):
    def on_message(self, message):
        self.write_message(str(predict(get_image_tensor_from_base64(message.split(',')[1]))).encode('utf8'))


if __name__ == "__main__":
    options.define("server_port", 8848, int, "Port to listen")
    options.define("server_prefix", "mnist", str, "The prefix of this application")
    options.define("server_address", type=str, help="IP or domain of your host")
    options.parse_command_line()
    if options.options.server_prefix[0] is not '/':
        prefix = '/' + options.options.server_prefix
    else:
        prefix = options.options.server_prefix
    app = web.Application([
        (prefix + "", MainHandler),
        (prefix + "/ws", DrawingHandler),
    ], template_path=os.path.join(rel_path, "page"), debug=True)
    print(tf.__version__, flush=True)
    app.listen(options.options.server_port)
    ioloop.IOLoop.instance().start()
