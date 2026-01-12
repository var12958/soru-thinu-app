import os
import json
import math
import argparse
import time
from pathlib import Path

import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator

ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = ROOT.parent
DATASET_DIR = ROOT / "dataset"
MODELS_DIR = ROOT / "models"
IMG_SIZE = (224, 224)
LEARNING_RATE = 1e-4


def discover_classes(dataset_dir: Path):
    classes = [p.name for p in sorted(dataset_dir.iterdir()) if p.is_dir()]
    return classes


def find_latest_checkpoint(models_dir: Path):
    latest = models_dir / "latest.keras"
    meta = models_dir / "latest_metadata.json"
    if latest.exists() and meta.exists():
        try:
            with open(meta, "r") as f:
                data = json.load(f)
            return latest, data
        except Exception:
            return None, None
    # fallback: look for epoch files
    epoch_files = sorted(models_dir.glob("food_model_epoch_*.keras"))
    if epoch_files:
        # pick last by name
        sol = epoch_files[-1]
        # no metadata about batch
        return sol, {"epoch": int(sol.stem.split("_")[-1]) - 0, "batch": 0}
    return None, None


def save_metadata(models_dir: Path, epoch: int, batch: int, extra=None):
    meta = {
        "epoch": epoch,
        "batch": batch,
        "timestamp": time.time()
    }
    if extra:
        meta.update(extra)
    with open(models_dir / "latest_metadata.json", "w") as f:
        json.dump(meta, f)


def build_model(num_classes: int):
    base_model = ResNet50(weights='imagenet', include_top=False, input_shape=IMG_SIZE + (3,))
    base_model.trainable = False
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(256, activation='relu')(x)
    x = Dropout(0.5)(x)
    predictions = Dense(num_classes, activation='softmax')(x)
    model = Model(inputs=base_model.input, outputs=predictions)
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    return model


def train(args):
    # Basic checks
    if not DATASET_DIR.exists():
        print(f"Error: Dataset directory not found at {DATASET_DIR}. Run ml/prepare_dataset.py first.")
        return

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # Discover classes dynamically
    classes = discover_classes(DATASET_DIR)
    if not classes:
        print("No class folders found inside dataset directory.")
        return

    print(f"Found {len(classes)} classes.")

    # Save class list
    with open(MODELS_DIR / "class_indices.json", "w") as f:
        json.dump(classes, f)

    # Data generators
    datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.1,
        height_shift_range=0.1,
        horizontal_flip=True,
        validation_split=0.2
    )

    train_gen = datagen.flow_from_directory(
        DATASET_DIR,
        target_size=IMG_SIZE,
        batch_size=args.batch_size,
        class_mode='categorical',
        subset='training'
    )

    val_gen = datagen.flow_from_directory(
        DATASET_DIR,
        target_size=IMG_SIZE,
        batch_size=args.batch_size,
        class_mode='categorical',
        subset='validation'
    )

    steps_per_epoch = math.ceil(train_gen.samples / args.batch_size)
    val_steps = math.ceil(val_gen.samples / args.batch_size) if val_gen.samples else 0

    # Build model
    model = build_model(len(classes))

    # Resume logic
    initial_epoch = 0
    resume_batch = 0
    if args.resume:
        ckpt, meta = find_latest_checkpoint(MODELS_DIR)
        if ckpt:
            try:
                print(f"Loading checkpoint {ckpt} ...")
                model = tf.keras.models.load_model(str(ckpt))
                if meta:
                    initial_epoch = int(meta.get("epoch", 0))
                    resume_batch = int(meta.get("batch", 0))
                print(f"Resuming from epoch {initial_epoch}, batch {resume_batch}")
            except Exception as e:
                print(f"Failed to load checkpoint: {e}")

    # Manual training loop with batch-level checkpoints
    total_epochs = args.epochs
    save_every = args.save_every_batches
    global_batch = initial_epoch * steps_per_epoch + resume_batch

    print(f"Training for {total_epochs} epochs | steps/epoch={steps_per_epoch} | validation_steps={val_steps}")

    for epoch in range(initial_epoch, total_epochs):
        print(f"\n--- Epoch {epoch+1}/{total_epochs} ---")
        batch_idx = 0
        # Reset generator and skip if resuming in middle of epoch
        train_gen.reset()

        # If resuming, skip batches
        if epoch == initial_epoch and resume_batch > 0:
            print(f"Skipping {resume_batch} batches to reach resume point...")
            for _ in range(resume_batch):
                try:
                    next(train_gen)
                except StopIteration:
                    break

        while batch_idx < steps_per_epoch:
            try:
                x_batch, y_batch = next(train_gen)
            except StopIteration:
                break

            loss, acc = model.train_on_batch(x_batch, y_batch)
            batch_idx += 1
            global_batch += 1

            # Print lightweight progress
            print(f"Epoch {epoch+1}/{total_epochs} - Batch {batch_idx}/{steps_per_epoch} - loss={loss:.4f} acc={acc:.4f}", end='\r')

            # periodic checkpoint
            if global_batch % save_every == 0:
                # save both readable epoch checkpoint and latest
                epoch_ckpt = MODELS_DIR / f"food_model_epoch_{epoch+1:03d}_batch_{batch_idx:06d}.keras"
                latest = MODELS_DIR / "latest.keras"
                try:
                    model.save(str(epoch_ckpt))
                    model.save(str(latest))
                    save_metadata(MODELS_DIR, epoch, batch_idx)
                    print(f"\nSaved checkpoint at epoch {epoch+1} batch {batch_idx}")
                except Exception as e:
                    print(f"\nFailed to save checkpoint: {e}")

        # Epoch end: run validation
        print()
        if val_steps > 0:
            print("Running validation...")
            val_res = model.evaluate(val_gen, steps=val_steps, verbose=1)
            print(f"Validation results: {val_res}")

        # Save epoch checkpoint
        try:
            epoch_file = MODELS_DIR / f"food_model_epoch_{epoch+1:03d}.keras"
            latest = MODELS_DIR / "latest.keras"
            model.save(str(epoch_file))
            model.save(str(latest))
            save_metadata(MODELS_DIR, epoch+1, 0)
            print(f"Saved end-of-epoch checkpoint: {epoch_file}")
        except Exception as e:
            print(f"Failed to save end-of-epoch checkpoint: {e}")

    # Training complete
    print("\nTraining complete. Finalizing artifacts...")

    # Nutrition lookups for each class
    try:
        import sys
        sys.path.insert(0, str(WORKSPACE_ROOT / 'backend'))
        from nutrition_apis import NutritionService
        svc = NutritionService()
        nutrition_info = {}
        for cls in classes:
            # Convert folder name to readable food name
            food_name = cls.replace('_', ' ')
            print(f"Fetching nutrition for {food_name}...")
            info = svc.get_nutrition_info(food_name)
            nutrition_info[cls] = info

        with open(MODELS_DIR / 'nutrition_info.json', 'w') as f:
            json.dump(nutrition_info, f, indent=2)
        print("Saved nutrition_info.json")
    except Exception as e:
        print(f"Nutrition lookup failed or not configured: {e}")

    print("Model trained and artifacts saved.")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--epochs', type=int, default=20)
    p.add_argument('--batch-size', type=int, default=32)
    p.add_argument('--save-every-batches', type=int, default=200, dest='save_every_batches')
    p.add_argument('--resume', action='store_true')
    return p.parse_args()


if __name__ == '__main__':
    args = parse_args()
    train(args)
