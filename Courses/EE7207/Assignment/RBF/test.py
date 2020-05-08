import numpy as np
from keras.models import Sequential
from keras.layers.core import Dense
from keras.optimizers import RMSprop, Adam
from rbflayer import RBFLayer, InitCentersRandom
import matplotlib.pyplot as plt


def load_data():
    # data = np.loadtxt("data/data.txt")
    # X = filter(lambda x: type(x) == 'float', data[:, :-1])
    # y = data[:, -1:]

    with open('data/data.txt') as f:
        data = f.readlines()
    
    # data processing
    split_data = [line.strip().split(',') for line in data]
    data = [[float(num) for num in line] for line in split_data]

    data = np.array(data)
    X = data[:, :-1]
    mean, std = np.mean(X, axis=0, keepdims=True), np.std(X, axis=0, keepdims=True)
    X = (X - mean) / std
    y = data[:, -1]
    y = (y + 1) / 2
    return X, y


if __name__ == "__main__":

    X, y = load_data()

    model = Sequential()
    rbflayer = RBFLayer(20,
                        initializer=InitCentersRandom(X),
                        betas=1.0,
                        input_shape=(X.shape[1],))
    model.add(rbflayer)
    model.add(Dense(1, activation='sigmoid', use_bias=False))

    model.compile(loss='binary_crossentropy',
                  optimizer=RMSprop(lr=0.001))

    model.fit(X, y,
              batch_size=50,
              epochs=2000,
              verbose=1)
    # model.save("some_fency_file_name.h5")

    y_pred = model.predict(X)

    # print(rbflayer.get_weights())

    total_num = X.shape[0]
    y_pred = np.squeeze(y_pred)
    plt.scatter(np.arange(total_num), y_pred, c='b', marker='x')
    plt.scatter(np.arange(total_num), y, c='r', marker='o')
    # plt.plot([-1, 1], [0, 0], color='black')
    # plt.xlim([-1, 1])
    model.save_weights('my_model_weights.h5')
    
    np.save('y_pred', y_pred)
    np.save('y', y)
    plt.show()
    
    #dense = model.get_weights(index=-1)
    #print(dense)
    # centers = rbflayer.get_weights()[0]
    # widths = rbflayer.get_weights()[1]
    # plt.scatter(centers, np.zeros(len(centers)), s=20*widths)

    # print('accurcy:', np.mean(y_pred.astype(np.int) == y.astype(np.int)))