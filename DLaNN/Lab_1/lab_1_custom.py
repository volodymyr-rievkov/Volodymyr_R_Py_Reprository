import os
import time
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from warnings import filterwarnings

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from keras.models import Sequential
from keras.layers import Dense
from keras.callbacks import EarlyStopping
from keras.utils import to_categorical

filterwarnings('ignore', category=UserWarning)

os.makedirs("DLaNN/Lab_1/data/plots_classification_custom", exist_ok=True)

def load_and_split_data(file_path, target_col):
    """
    Loads data and splits it into Train (70%), Validation (20%), and Test (10%).
    """
    df = pd.read_csv(file_path)
    X = df.drop(columns=[target_col])
    X = pd.get_dummies(X, drop_first=True)

    le = LabelEncoder()
    y_encoded = le.fit_transform(df[target_col])
    y = to_categorical(y_encoded)
    
    # Step 1: Split 70% for training, 30% for temp (validation + test)
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # Step 2: Split the 30% temp data into Validation (20% of total) and Test (10% of total)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=1/3, random_state=42)
    
    print(f"[INFO] Data split complete: Train={len(X_train)} (70%), Val={len(X_val)} (20%), Test={len(X_test)} (10%)")
    return X_train, X_val, X_test, y_train, y_val, y_test

def scale_features(X_train, X_val, X_test):
    """
    Scales only the input features using StandardScaler.
    """
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    
    print("[INFO] Features successfully scaled.")
    return X_train_scaled, X_val_scaled, X_test_scaled

def build_model(input_dim, layers, optimizer='adam', activation='relu'):
    """
    Builds a Sequential Keras model with a dynamically defined number of hidden layers.
    """
    model = Sequential()
    
    # Input layer + First hidden layer
    model.add(Dense(layers[0], activation=activation, input_shape=(input_dim,)))
    
    # Additional hidden layers based on the 'layers' list
    for neurons in layers[1:]:
        model.add(Dense(neurons, activation=activation))
        
    # Output layer for classification (2 nodes for binary classes, softmax)
    model.add(Dense(2, activation='softmax'))
    
    model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def train_and_evaluate_model(model, X_train, y_train, X_val, y_val, X_test, y_test, epochs=50):
    """
    Trains the model with Early Stopping and evaluates it on the test set.
    """
    start_time = time.time()
    early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
    
    history = model.fit(
        X_train, y_train, 
        validation_data=(X_val, y_val), 
        epochs=epochs, 
        callbacks=[early_stopping], 
        verbose=0
    )
    
    test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
    duration = time.time() - start_time
    
    print(f"[INFO] Model trained in {duration:.2f} seconds.")
    return history, test_loss, test_acc, duration

def plot_learning_curves(histories_dict, title, filename):
    """
    Helper function to plot and save validation accuracy comparisons.
    """
    plt.figure(figsize=(10, 6))
    
    for label, history in histories_dict.items():
        val_acc = history.history['val_accuracy']
        max_val_acc = max(val_acc)
        plt.plot(val_acc, label=f"{label} (Max Acc: {max_val_acc:.4f})")
        
    plt.title(title)
    plt.xlabel('Epochs')
    plt.ylabel('Validation Accuracy')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'DLaNN/Lab_1/data/plots_classification_custom/{filename}')
    plt.close()
    print(f"[INFO] Plot saved to 'data/plots_classification_custom/{filename}")

def plot_duration_histogram(durations, title, filename):
    plt.figure(figsize=(10, 5))
    names = list(durations.keys())
    times = [durations[n] for n in names]
    plt.bar(names, times, color='skyblue', edgecolor='navy')
    plt.title(title)
    plt.ylabel('Seconds')
    plt.savefig(f'DLaNN/Lab_1/data/plots_classification_custom/{filename}')
    plt.close()

def plot_overfitting_analysis(history, title, filename):
    """
    Plots training and validation accuracy to identify overfitting.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(history.history['accuracy'], label='Training Accuracy', color='blue', linewidth=2)
    plt.plot(history.history['val_accuracy'], label='Validation Accuracy', color='orange', linewidth=2)
    plt.title(title)
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig(f'DLaNN/Lab_1/data/plots_classification_custom/{filename}')
    plt.close()
    print(f"[INFO] Overfitting analysis plot saved to 'data/plots_classification_custom/{filename}")

def run_optimizer_experiment(X_train, y_train, X_val, y_val, X_test, y_test, layers):
    """
    Runs experiments to compare different optimizers.
    """
    print("\n--- Starting Optimizer Experiment ---")
    optimizers = ['adam', 'sgd', 'rmsprop', 'adadelta', 'adagrad', 'adamax', 'nadam']
    histories = {}
    durations = {}
    
    for opt in optimizers:
        print(f"[RUNNING] Training with optimizer: {opt.upper()}...")
        model = build_model(X_train.shape[1], layers=layers, optimizer=opt, activation='relu')
        
        history, test_loss, test_acc, duration = train_and_evaluate_model(
            model, X_train, y_train, X_val, y_val, X_test, y_test
        )
        
        histories[opt.upper()] = history
        durations[opt.upper()] = duration
        print(f"   [RESULT] {opt.upper()} -> Test Loss: {test_loss:.4f} | Test Acc: {test_acc:.4f}")
        plot_overfitting_analysis(history, f'Overfitting Analysis ({opt.upper()})', f'overfitting_{opt}.png')

    plot_duration_histogram(durations, 'Optimizer Comparison (Training Duration)', 'optimizer_duration.png')
    plot_learning_curves(histories, 'Optimizer Comparison (Validation Accuracy)', 'optimizer_comparison.png')

def run_activation_experiment(X_train, y_train, X_val, y_val, X_test, y_test, layers):
    """
    Runs experiments to compare different activation functions.
    """
    print("\n--- Starting Activation Experiment ---")
    activations = ['relu', 'tanh', 'sigmoid']
    histories = {}
    
    for act in activations:
        print(f"[RUNNING] Training with activation: {act}...")
        model = build_model(X_train.shape[1], layers=layers, optimizer='adam', activation=act)
        
        history, test_loss, test_acc, _ = train_and_evaluate_model(
            model, X_train, y_train, X_val, y_val, X_test, y_test
        )
        
        histories[act] = history
        print(f"   [RESULT] {act} -> Test Loss: {test_loss:.4f} | Test Acc: {test_acc:.4f}")
        
    plot_learning_curves(histories, 'Activation Function Comparison (Optimizer: Adam)', 'activation_comparison.png')

if __name__ == "__main__":
    DATA_FILE = 'DLaNN/Lab_1/data/mushrooms.csv'
    TARGET = 'class'
    
    NETWORK_LAYERS = [32, 16]
    
    try:
        X_tr, X_va, X_te, y_tr, y_va, y_te = load_and_split_data(DATA_FILE, TARGET)
    except FileNotFoundError:
        print(f"[ERROR] File '{DATA_FILE}' not found. Please ensure it is in the correct directory.")
        exit(1)
        
    X_tr, X_va, X_te = scale_features(X_tr, X_va, X_te)
    
    run_optimizer_experiment(X_tr, y_tr, X_va, y_va, X_te, y_te, NETWORK_LAYERS)
    run_activation_experiment(X_tr, y_tr, X_va, y_va, X_te, y_te, NETWORK_LAYERS)
    
    print("\n[SUCCESS] All experiments completed successfully!")