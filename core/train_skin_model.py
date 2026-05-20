import pandas as pd
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report


def train_skin_model():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "datasets", "Electrical.csv")

    if not os.path.exists(csv_path):
        print("Dataset not found")
        return

    df = pd.read_csv(csv_path)
    print("Columns:", df.columns.tolist())
    print(df.head())

    X = df[[
        "Electrical_Capacitance",
        "Skin_Temperature",
        "Skin_Conductance",
        "Ambient_Humidity",
        "Ambient_Temperature",
        "Time_of_Day"
    ]]

    y = df["Target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)

    print("\nTraining Skin Model...")
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("\nAccuracy:", round(accuracy_score(y_test, y_pred), 2))
    print(classification_report(y_test, y_pred))

    # Save in core/models/
    models_dir = os.path.join(base_dir, "models")
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, "skin_model.pkl")
    joblib.dump(model, model_path)
    print("\nModel saved:", model_path)


if __name__ == "__main__":
    train_skin_model()