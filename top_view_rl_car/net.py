import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import Sequential
from tensorflow.keras.layers import LSTM, Dense, InputLayer

# physical_devices = tf.config.list_physical_devices('GPU')
# tf.config.experimental.set_memory_growth(physical_devices[0], True)


def make_lstm_qdn(n_inputs: int, n_steps: int, n_outputs: int, n_hidden_units: int) -> keras.Model:
    model = Sequential()
    model.add(InputLayer(input_shape=(n_steps, n_inputs)))
    model.add(LSTM(units=n_hidden_units))
    model.add(Dense(units=n_outputs))
    model.compile('adam', 'mse')
    return model
