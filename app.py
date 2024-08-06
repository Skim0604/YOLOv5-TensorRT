import sys
import cv2
import imutils
import serial
from yoloProc import YoloTRT

# Inisialisasi komunikasi serial
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)  # Sesuaikan port dan baud rate

# Inisialisasi model YOLO
model = YoloTRT(library="yolov5/build/libmyplugins.so", engine="yolov5/build/trainYoloV5s.engine", conf=0.5)

cap = cv2.VideoCapture(0)  # Kamera webcam

while True:
    ret, frame = cap.read()
    # Rotasi frame 180 derajat
    frame = cv2.rotate(frame, cv2.ROTATE_180)
    frame = imutils.resize(frame, width=600)
    detections, t = model.Inference(frame)
    
    
    for obj in detections:
        # Inisialisasi koordinat default
        center_x, center_y = -1, -1
        print(obj['class'], obj['conf'], obj['box'])
        
        if obj['class'] == "KORBAN":
            x1, y1, x2, y2 = obj['box']
            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)
            cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)  # Menampilkan titik tengah dengan lingkaran merah
            print("Koordinat: ", (center_x, center_y))
             
        # Kirim data koordinat ke ESP32 melalui serial
        data_to_send = f"{center_x},{center_y}\n"
        ser.write(data_to_send.encode())
    

    print("FPS: {} sec".format(1/t))

    # Baca data dari ESP32
    if ser.in_waiting > 0:
        data_received = ser.readline().decode().strip()
        if data_received == "STOP":
            print("Stop scan command received.")
            break

    #cv2.imshow("Deteksi Objek", frame)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
ser.close()  # Tutup koneksi serial saat selesai
