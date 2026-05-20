import pandas as pd
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report


def train_body_hydration_model():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "datasets", "Daily_Water_Intake.csv")

    if not os.path.exists(csv_path):
        print("Dataset not found:", csv_path)
        return

    df = pd.read_csv(csv_path)
    print("Columns found:", df.columns.tolist())

    # Rename columns to standard names
    df = df.rename(columns={
        "Weight (kg)":                  "Weight",
        "Daily Water Intake (liters)":  "Daily_Water_Intake",
        "Physical Activity Level":      "Physical_Activity",
        "Hydration Level":              "Hydration_Level"
    })

    categorical_cols = ["Gender", "Physical_Activity", "Weather"]
    numeric_cols     = ["Age", "Weight", "Daily_Water_Intake"]
    target_col       = "Hydration_Level"

    X = df[categorical_cols + numeric_cols]
    y = df[target_col]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols)
        ],
        remainder="passthrough"
    )

    model = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            class_weight='balanced'
        ))
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print("\nTraining model...")
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("\nAccuracy:", round(accuracy_score(y_test, y_pred), 2))
    print("\nClassification Report:\n")
    print(classification_report(y_test, y_pred))

    # Save inside core/models/
    models_dir = os.path.join(base_dir, "models")
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, "body_hydration_model.pkl")
    joblib.dump(model, model_path)
    print("\nModel saved:", model_path)


if __name__ == "__main__":
    train_body_hydration_model()