import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging
import warnings

import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from sklearn.model_selection import train_test_split
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPool2D
from keras.optimizers import RMSprop, Adam, SGD
from keras.src.legacy.preprocessing.image import ImageDataGenerator

# Turn off warnings
warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_and_preprocess_datasets(train_path, test_path):
    """Load and normalize datasets."""
    logger.info("Loading datasets...")
    train = pd.read_csv(train_path)
    test = pd.read_csv(test_path)
    
    # Train data
    Y_train = train["label"]
    X_train = train.drop(labels=["label"], axis=1)
    
    # Normalization (0-1)
    X_train = X_train / 255.0
    X_test = test / 255.0
    
    # Reshape in 3D tensors (28x28x1)
    X_train = X_train.values.reshape(-1, 28, 28, 1)
    X_test = X_test.values.reshape(-1, 28, 28, 1)
    
    # One-hot encoding for labels
    Y_train = to_categorical(Y_train, num_classes=10)
    
    # Розбиття на train та validation (90/10)
    X_train, X_val, Y_train, Y_val = train_test_split(X_train, Y_train, test_size=0.1, random_state=2)
    
    logger.info(f"Datasets loaded. Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")
    return X_train, X_val, Y_train, Y_val, X_test


def build_model(kernel_sizes=[(5,5), (3,3)], add_extra_conv=False):
    """Dynamic model builder regarding passed params."""
    model = Sequential()
    
    model.add(Conv2D(filters=8, kernel_size=kernel_sizes[0], padding='same', 
                     activation='relu', input_shape=(28,28,1)))
    model.add(MaxPool2D(pool_size=(2,2)))
    model.add(Dropout(0.25))
    
    model.add(Conv2D(filters=16, kernel_size=kernel_sizes[1], padding='same', activation='relu'))
    model.add(MaxPool2D(pool_size=(2,2), strides=(2,2)))
    model.add(Dropout(0.25))
    
    if add_extra_conv:
        k_size = kernel_sizes[-1] if len(kernel_sizes) > 2 else (3,3)
        model.add(Conv2D(filters=32, kernel_size=k_size, padding='same', activation='relu'))
        model.add(MaxPool2D(pool_size=(2,2), strides=(2,2), padding='same'))
        model.add(Dropout(0.25))
        
    model.add(Flatten())
    model.add(Dense(256, activation="relu"))
    model.add(Dropout(0.5))
    model.add(Dense(10, activation="softmax"))
    
    return model


def run_experiment(experiment_name, config, X_train, Y_train, X_val, Y_val):
    """Runs experiment with passed params."""
    logger.info(f"--- Starting experiment: {experiment_name} ---")
    
    model = build_model(kernel_sizes=config.get('kernel_sizes', [(5,5), (3,3)]), 
                        add_extra_conv=config.get('extra_conv', False))
    
    opt_name = config.get('optimizer', 'adam').lower()
    lr = config.get('learning_rate', 0.001)
    
    if opt_name == 'adam': optimizer = Adam(learning_rate=lr)
    elif opt_name == 'rmsprop': optimizer = RMSprop(learning_rate=lr)
    else: optimizer = SGD(learning_rate=lr, momentum=0.9)
        
    model.compile(optimizer=optimizer, loss="categorical_crossentropy", metrics=["accuracy"])
    
    datagen = ImageDataGenerator(**config.get('aug_params', {}))
    datagen.fit(X_train)
    
    epochs = config.get('epochs', 10)
    batch_size = config.get('batch_size', 250)
    
    # Learn
    history = model.fit(datagen.flow(X_train, Y_train, batch_size=batch_size),
                        epochs=epochs, 
                        validation_data=(X_val, Y_val),
                        steps_per_epoch=X_train.shape[0] // batch_size,
                        verbose=0)
    
    val_loss, val_acc = model.evaluate(X_val, Y_val, verbose=0)
    logger.info(f"Finished experiment: {experiment_name} | Val Acc: {val_acc:.4f} | Val Loss: {val_loss:.4f}")
    
    return history.history, model, val_acc


def plot_experiment_metrics(results_dict):
    """Buids and saves comparison plot for Validation Accuracy and Validation Loss."""
    plt.figure(figsize=(16, 6))
    
    # Accuracy plot
    plt.subplot(1, 2, 1)
    for exp_name, data in results_dict.items():
        plt.plot(data['history']['val_accuracy'], label=exp_name, marker='o')
    plt.title('Validation Accuracy Comparsion')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True)
    
    # Графік Loss
    plt.subplot(1, 2, 2)
    for exp_name, data in results_dict.items():
        plt.plot(data['history']['val_loss'], label=exp_name, marker='x')
    plt.title('Validation Loss Comparsion')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('./DLaNN/Lab_2/data/accuracy_loss_comparison.png')
    plt.close()


def create_submission(best_model, X_test):
    """Generate submission csv"""
    logger.info("Generating submission csv...")
    predictions = best_model.predict(X_test)
    # Collect prediction with biggest probability
    results = np.argmax(predictions, axis=1)
    
    # Create dataframe
    submission = pd.DataFrame({
        "ImageId": range(1, len(results) + 1),
        "Label": results
    })
    submission.to_csv("./DLaNN/Lab_2/data/best_submission.csv", index=False)
    logger.info("Submission csv created.")


if __name__ == "__main__":
    X_train, X_val, Y_train, Y_val, X_test = load_and_preprocess_datasets("./DLaNN/Lab_2/data/train.csv", "./DLaNN/Lab_2/data/test.csv")
    
    experiment_results = {}
    
    base_config = {
        'epochs': 8, 'batch_size': 250, 'optimizer': 'adam', 'extra_conv': False,
        'kernel_sizes': [(5,5), (3,3)], 'aug_params': {'rotation_range': 10, 'zoom_range': 0.1}
    }
    
    # Base experiment
    hist, model, acc = run_experiment("Base CNN (Adam, 5x5+3x3)", base_config, X_train, Y_train, X_val, Y_val)
    experiment_results["Base"] = {'history': hist, 'model': model, 'val_acc': acc}
    

    cfg_opt = base_config.copy()
    cfg_opt['optimizer'] = 'rmsprop'

    # RMSprop as optimizer experiment
    hist, model, acc = run_experiment("RMSprop Opt", cfg_opt, X_train, Y_train, X_val, Y_val)
    experiment_results["RMSprop"] = {'history': hist, 'model': model, 'val_acc': acc}
    

    cfg_kern = base_config.copy()
    cfg_kern['kernel_sizes'] = [(5,3), (3,5)]
    # Rectangular kernels experiment
    hist, model, acc = run_experiment("Rectangular Kernels", cfg_kern, X_train, Y_train, X_val, Y_val)
    experiment_results["Rect Kernels"] = {'history': hist, 'model': model, 'val_acc': acc}
    

    cfg_deep = base_config.copy()
    cfg_deep['extra_conv'] = True
    # Additional Conv Layer experiment
    hist, model, acc = run_experiment("Extra Conv Layer", cfg_deep, X_train, Y_train, X_val, Y_val)
    experiment_results["Deep Net"] = {'history': hist, 'model': model, 'val_acc': acc}
    

    logger.info("Plotting experiment metrics...")
    plot_experiment_metrics(experiment_results)
    
    # Select best experiment
    best_exp_name = max(experiment_results, key=lambda k: experiment_results[k]['val_acc'])
    best_model = experiment_results[best_exp_name]['model']
    
    logger.info(f"Best model: {best_exp_name} with Validation Accuracy: {experiment_results[best_exp_name]['val_acc']:.4f}")
    
    create_submission(best_model, X_test)