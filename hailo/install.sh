#!/bin/bash

# Source environment variables and activate virtual environment
source setup_env.sh

# Install the required Python dependencies
pip install -r requirements.txt 

#pip install -r tests/test_resources/requirements.txt

# Install additional system dependencies (if needed)
sudo apt install -y rapidjson-dev

# Check if the --all flag is provided
DOWNLOAD_RESOURCES_FLAG=""
if [[ "$1" == "--all" ]]; then
    DOWNLOAD_RESOURCES_FLAG="--all"
fi

# Download resources needed for the pipelines
#./download_resources.sh $DOWNLOAD_RESOURCES_FLAG

download_model() {
  wget -nc "$1" -P ./resources
}

H8_HEFS=(
  "https://hailo-model-zoo.s3.eu-west-2.amazonaws.com/ModelZoo/Compiled/v2.13.0/hailo8/yolov8m_pose.hef"
  "https://hailo-model-zoo.s3.eu-west-2.amazonaws.com/ModelZoo/Compiled/v2.13.0/hailo8/yolov8s_pose.hef"
)
H8L_HEFS=(
  "https://hailo-csdata.s3.eu-west-2.amazonaws.com/resources/hefs/h8l_rpi/yolov8s_pose_h8l.hef"
)

if [ "$DEVICE_ARCHITECTURE" == "HAILO8L" ]; then
  echo "Downloading HAILO8L models"
  for url in "${H8L_HEFS[@]}"; do
    download_model "$url"
  done
fi
if [ "$DEVICE_ARCHITECTURE" == "HAILO8" ]; then
  echo "Downloading HAILO8 models"
  for url in "${H8_HEFS[@]}"; do
    download_model "$url"
  done
fi

# Optional: Post-process compilation (Only for older TAPPAS versions)
./compile_postprocess.sh
