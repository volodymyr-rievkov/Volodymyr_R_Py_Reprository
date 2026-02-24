import os
import time
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from warnings import filterwarnings

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.callbacks import EarlyStopping

filterwarnings('ignore', category=UserWarning)

os.makedirs("data/plots_regression", exist_ok=True)

def load_and_split_data(file_path, target_col):
    """
    Loads data and splits it into Train (70%), Validation (20%), and Test (10%).
    """
    df = pd.read_csv(file_path)
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    # Step 1: Split 70% for training, 30% for temp (validation + test)
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # Step 2: Split the 30% temp data into Validation (20% of total) and Test (10% of total)
    # 1/3 of 30% is 10%, 2/3 of 30% is 20%
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=1/3, random_state=42)
    
    print(f"[INFO] Data split complete: Train={len(X_train)} (70%), Val={len(X_val)} (20%), Test={len(X_test)} (10%)")
    return X_train, X_val, X_test, y_train, y_val, y_test

def scale_features(X_train, X_val, X_test):
    """
    Scales only the input features using StandardScaler. 
    Target variable (y) remains unscaled for interpretable MAE (e.g., in dollars).
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
        
    # Output layer for regression (1 node, no activation function)
    model.add(Dense(1))
    
    model.compile(optimizer=optimizer, loss='mean_squared_error', metrics=['mae'])
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
        verbose=0 # Suppress epoch-by-epoch output
    )
    
    test_loss, test_mae = model.evaluate(X_test, y_test, verbose=0)
    duration = time.time() - start_time
    
    print(f"[INFO] Model trained in {duration:.2f} seconds.")
    return history, test_loss, test_mae, duration

def plot_learning_curves(histories_dict, title, filename):
    """
    Helper function to plot and save validation loss comparisons.
    """
    plt.figure(figsize=(10, 6))
    
    for label, history in histories_dict.items():
        val_loss = history.history['val_loss']
        min_val_loss = min(val_loss)
        plt.plot(val_loss, label=f"{label} (Min MSE: {min_val_loss:.2f})")
        
    plt.title(title)
    plt.xlabel('Epochs')
    plt.ylabel('Validation Loss (MSE)')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'data/plots_regression/{filename}')
    plt.close()
    print(f"[INFO] Plot saved to 'data/plots_regression/{filename}")

def plot_duration_histogram(durations, title, filename):
    plt.figure(figsize=(10, 5))
    names = list(durations.keys())
    times = [durations[n] for n in names]
    plt.bar(names, times, color='skyblue', edgecolor='navy')
    plt.title(title)
    plt.ylabel('Seconds')
    plt.savefig(f'data/plots_regression/{filename}')
    plt.close()

def plot_overfitting_analysis(history, title, filename):
    """
    Plots training and validation loss to identify overfitting.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(history.history['loss'], label='Training Loss (MSE)', color='blue', linewidth=2)
    plt.plot(history.history['val_loss'], label='Validation Loss (MSE)', color='orange', linewidth=2)
    plt.title(title)
    plt.xlabel('Epochs')
    plt.ylabel('Loss (MSE)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig(f'data/plots_regression/{filename}')
    plt.close()
    print(f"[INFO] Overfitting analysis plot saved to 'data/plots_regression/{filename}")

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
        
        history, test_loss, test_mae, duration = train_and_evaluate_model(
            model, X_train, y_train, X_val, y_val, X_test, y_test
        )
        
        histories[opt.upper()] = history
        durations[opt.upper()] = duration
        print(f"   [RESULT] {opt.upper()} -> Test MSE: {test_loss:.2f} | Test MAE: {test_mae:.2f}")
        plot_overfitting_analysis(history, f'Overfitting Analysis ({opt.upper()})', f'overfitting_{opt}.png')

    plot_duration_histogram(durations, 'Optimizer Comparison (Training Duration)', 'optimizer_duration.png')
    plot_learning_curves(histories, 'Optimizer Comparison (Validation Loss)', 'optimizer_comparison.png')

def run_activation_experiment(X_train, y_train, X_val, y_val, X_test, y_test, layers):
    """
    Runs experiments to compare different activation functions using the Adam optimizer.
    """
    print("\n--- Starting Activation Experiment ---")
    activations = ['relu', 'tanh', 'sigmoid']
    histories = {}
    
    for act in activations:
        print(f"[RUNNING] Training with activation: {act}...")
        model = build_model(X_train.shape[1], layers=layers, optimizer='adam', activation=act)
        
        history, test_loss, test_mae, _ = train_and_evaluate_model(
            model, X_train, y_train, X_val, y_val, X_test, y_test
        )
        
        histories[act] = history
        print(f"   [RESULT] {act} -> Test MSE: {test_loss:.2f} | Test MAE: {test_mae:.2f}")
        
    plot_learning_curves(histories, 'Activation Function Comparison (Optimizer: Adam)', 'activation_comparison.png')

if __name__ == "__main__":
    # Define dataset path and target column
    DATA_FILE = 'data/hourly_wages_data.csv'
    TARGET = 'wage_per_hour'
    
    # Define architecture
    NETWORK_LAYERS = [64, 32]
    
    # 1. Prepare data
    try:
        X_tr, X_va, X_te, y_tr, y_va, y_te = load_and_split_data(DATA_FILE, TARGET)
    except FileNotFoundError:
        print(f"[ERROR] File '{DATA_FILE}' not found. Please ensure it is in the correct directory.")
        exit(1)
        
    # 2. Scale features
    X_tr, X_va, X_te = scale_features(X_tr, X_va, X_te)
    
    # 3. Run Experiments
    run_optimizer_experiment(X_tr, y_tr, X_va, y_va, X_te, y_te, NETWORK_LAYERS)
    run_activation_experiment(X_tr, y_tr, X_va, y_va, X_te, y_te, NETWORK_LAYERS)
    
    print("\n[SUCCESS] All experiments completed successfully!")