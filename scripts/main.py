import sys

sys.path.append("..")

# from training import pretrain_parking_sensor_encoder_with_icm
from training import train_to_steer_on_parking_sensors

if __name__ == "__main__":
    # pretrain_parking_sensor_encoder_with_icm()
    train_to_steer_on_parking_sensors()