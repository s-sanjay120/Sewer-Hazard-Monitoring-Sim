import joblib
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

data_dir = Path(__file__).resolve().parent.parent / "data"
model_dir = Path(__file__).resolve().parent.parent / "models"
BASE_DIR = Path(__file__).resolve().parent
SEQUENCE_LENGTH = 10
EPOCHS = 20
BATCH_SIZE = 32
RANDOM_SEED = 42


def load_dataset() -> pd.DataFrame:
    candidates = [
        data_dir / "sensor_data.csv"
    ]

    for path in candidates:
        if path.exists():
            df = pd.read_csv(path)
            break
    else:
        raise FileNotFoundError("No training dataset found. Expected one of: new_synthetic_data_with_time.csv, data/gas_readings.csv, data/time_series.csv")

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")

    preferred_columns = ["methane", "air_quality", "temperature", "humidity"]
    feature_columns = [col for col in preferred_columns if col in df.columns]

    if not feature_columns:
        numeric_columns = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col]) and col.lower() != "risk"]
        feature_columns = numeric_columns

    if not feature_columns:
        raise ValueError("No numeric feature columns were found in the dataset")

    return df[feature_columns].astype(float)


def create_sequences(data: np.ndarray, sequence_length: int):
    X, y = [], []
    for i in range(sequence_length, len(data)):
        X.append(data[i - sequence_length:i])
        y.append(data[i])
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)


class LSTMRegressor(nn.Module):
    def __init__(self, input_size: int, hidden_size: int = 64, output_size: int = 4):
        super().__init__()
        self.lstm = nn.LSTM(input_size=input_size, hidden_size=hidden_size, batch_first=True)
        self.fc1 = nn.Linear(hidden_size, 32)
        self.fc2 = nn.Linear(32, output_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x, _ = self.lstm(x)
        x = x[:, -1, :]
        x = torch.relu(self.fc1(x))
        return self.fc2(x)


def main():
    np.random.seed(RANDOM_SEED)
    torch.manual_seed(RANDOM_SEED)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on: {device}")

    data = load_dataset()
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data)
    joblib.dump(scaler, model_dir / "lstm_scaler.pkl")

    X, y = create_sequences(scaled_data, SEQUENCE_LENGTH)
    print(f"Input shape: {X.shape}")
    print(f"Target shape: {y.shape}")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=RANDOM_SEED,
    )

    train_dataset = TensorDataset(
        torch.tensor(X_train, dtype=torch.float32),
        torch.tensor(y_train, dtype=torch.float32),
    )
    test_dataset = TensorDataset(
        torch.tensor(X_test, dtype=torch.float32),
        torch.tensor(y_test, dtype=torch.float32),
    )

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

    model = LSTMRegressor(input_size=data.shape[1], output_size=data.shape[1]).to(device)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    for epoch in range(EPOCHS):
        model.train()
        running_loss = 0.0

        for sequences, targets in train_loader:
            sequences = sequences.to(device)
            targets = targets.to(device)

            optimizer.zero_grad()
            predictions = model(sequences)
            loss = criterion(predictions, targets)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * sequences.size(0)

        avg_train_loss = running_loss / len(train_dataset)
        print(f"Epoch {epoch + 1}/{EPOCHS} - loss: {avg_train_loss:.6f}")

    model.eval()
    test_loss = 0.0
    with torch.no_grad():
        for sequences, targets in test_loader:
            sequences = sequences.to(device)
            targets = targets.to(device)
            predictions = model(sequences)
            test_loss += criterion(predictions, targets).item() * sequences.size(0)

    test_loss /= len(test_dataset)
    print(f"Test loss: {test_loss:.6f}")

    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "input_size": data.shape[1],
            "sequence_length": SEQUENCE_LENGTH,
            "feature_columns": list(data.columns),
        },
        model_dir / "lstm_model.pth",
    )
    print(f"Saved PyTorch model to {model_dir / 'lstm_model.pth'}")


if __name__ == "__main__":
    main()
