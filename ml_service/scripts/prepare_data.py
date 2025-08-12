import os
import shutil
from sklearn.model_selection import train_test_split

DATA_PATH = "data"
OUTPUT_DIR = "data/merged_dataset"

VAL_SPLIT = 0.2
TEST_SPLIT = 0.1

def create_dir(path):
    os.makedirs(path, exist_ok=True)

def copy_images(src_list, dst_dir):
    for img_path in src_list:
        shutil.copy(img_path, dst_dir)

def split_data(image_list):
    # First split out test set
    train_val, test = train_test_split(image_list, test_size=TEST_SPLIT)
    # Then split train_val into train and val
    train, val = train_test_split(train_val, test_size=VAL_SPLIT)
    return train, val, test

def prepare_dataset():
    for split in ["train", "val", "test"]:
        for cls in ["normal", "tb", "pneumonia"]:
            create_dir(os.path.join(OUTPUT_DIR, split, cls))

    # Load image paths
    tb_images = [os.path.join(DATA_PATH, "tb", f) for f in os.listdir(os.path.join(DATA_PATH, "tb"))]
    normal_images = [os.path.join(DATA_PATH, "normal", f) for f in os.listdir(os.path.join(DATA_PATH, "normal"))]
    pneumonia_images = [os.path.join(DATA_PATH, "pneumonia", f) for f in os.listdir(os.path.join(DATA_PATH, "pneumonia"))]

    tb_train, tb_val, tb_test = split_data(tb_images)
    normal_train, normal_val, normal_test = split_data(normal_images)
    pneumonia_train, pneumonia_val, pneumonia_test = split_data(pneumonia_images)

    # Copy to train
    copy_images(tb_train, os.path.join(OUTPUT_DIR, "train", "tb"))
    copy_images(normal_train, os.path.join(OUTPUT_DIR, "train", "normal"))
    copy_images(pneumonia_train, os.path.join(OUTPUT_DIR, "train", "pneumonia"))

    # Copy to val
    copy_images(tb_val, os.path.join(OUTPUT_DIR, "val", "tb"))
    copy_images(normal_val, os.path.join(OUTPUT_DIR, "val", "normal"))
    copy_images(pneumonia_val, os.path.join(OUTPUT_DIR, "val", "pneumonia"))

    # Copy to test
    copy_images(tb_test, os.path.join(OUTPUT_DIR, "test", "tb"))
    copy_images(normal_test, os.path.join(OUTPUT_DIR, "test", "normal"))
    copy_images(pneumonia_test, os.path.join(OUTPUT_DIR, "test", "pneumonia"))

    print(f"✅ Dataset prepared in {OUTPUT_DIR}")

if __name__ == "__main__":
    prepare_dataset()
