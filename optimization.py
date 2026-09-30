import os
import cv2
import time
import wave
import threading
import pyaudio

from datetime import datetime, timezone

import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv


# ============================================================
# DAY 29 - LOCAL SYSTEM OPTIMIZATION
# ============================================================

load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

EMPLOYEE_ID = os.getenv(
    "EMPLOYEE_ID",
    "EMP001"
)

SERVICE_ACCOUNT_FILE = "serviceAccountKey.json"

FIREBASE_COLLECTION = "day29_optimization_logs"

# Video configuration
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 480

# Audio configuration
AUDIO_RATE = 16000
AUDIO_CHANNELS = 1
AUDIO_CHUNK = 1024

# Local audio output
AUDIO_FILE = "day29_audio.wav"


stop_event = threading.Event()


def initialize_firebase():

    try:

        if not os.path.exists(
            SERVICE_ACCOUNT_FILE
        ):

            print(
                "[FIREBASE] serviceAccountKey.json "
                "not found."
            )

            return None

        # Initialize Firebase only once
        if not firebase_admin._apps:

            credential = credentials.Certificate(
                SERVICE_ACCOUNT_FILE
            )

            firebase_admin.initialize_app(
                credential
            )

        db = firestore.client()

        print(
            "[FIREBASE] Connected successfully."
        )

        return db

    except Exception as error:

        print(
            "[FIREBASE] Connection failed:"
        )

        print(error)

        return None

class VideoOptimizer:

    def __init__(self):

        self.total_frames = 0
        self.processed_frames = 0

        self.total_processing_time = 0.0

        self.start_time = None

        self.fps = 0.0

    def run(self):

        print("\n[VIDEO] Starting webcam...")

        camera = cv2.VideoCapture(0)

        if not camera.isOpened():

            print(
                "[VIDEO] ERROR: "
                "Unable to open webcam."
            )

            stop_event.set()

            return

    
        camera.set(
            cv2.CAP_PROP_BUFFERSIZE,
            1
        )


        camera.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            VIDEO_WIDTH
        )

        camera.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            VIDEO_HEIGHT
        )

        self.start_time = time.perf_counter()

        print(
            "[VIDEO] Optimization started."
        )

        while not stop_event.is_set():

            frame_start = time.perf_counter()

            success, frame = camera.read()

            if not success:

                print(
                    "[VIDEO] Frame capture failed."
                )

                continue

            self.total_frames += 1

    
            frame = cv2.resize(
                frame,
                (
                    VIDEO_WIDTH,
                    VIDEO_HEIGHT
                ),
                interpolation=cv2.INTER_AREA
            )

        
            gray_frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY
            )

    

            processing_time = (
                time.perf_counter()
                - frame_start
            )

            self.total_processing_time += (
                processing_time
            )

            self.processed_frames += 1

    

            elapsed = (
                time.perf_counter()
                - self.start_time
            )

            if elapsed > 0:

                self.fps = (
                    self.processed_frames
                    / elapsed
                )

           

            cv2.putText(
                gray_frame,
                f"FPS: {self.fps:.2f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                255,
                2
            )

            cv2.putText(
                gray_frame,
                f"Frames: {self.processed_frames}",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                255,
                2
            )

            cv2.putText(
                gray_frame,
                "Press Q to stop",
                (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                255,
                2
            )

            cv2.imshow(
                "Day 29 - Video Optimization",
                gray_frame
            )

    
            if (
                cv2.waitKey(1) & 0xFF
            ) == ord("q"):

                stop_event.set()

                break

        camera.release()

        cv2.destroyAllWindows()

        print(
            "[VIDEO] Optimization stopped."
        )

    def get_result(self):

        if self.processed_frames > 0:

            average_processing_time = (
                self.total_processing_time
                / self.processed_frames
            )

        else:

            average_processing_time = 0

        return {

            "total_frames":
                self.total_frames,

            "processed_frames":
                self.processed_frames,

            "fps":
                round(
                    self.fps,
                    2
                ),

            "average_frame_processing_time":
                round(
                    average_processing_time,
                    4
                )
        }

class AudioOptimizer:

    def __init__(self):

        self.audio = None
        self.stream = None

        self.audio_chunks = 0

        self.total_latency = 0.0

        self.maximum_latency = 0.0

        self.audio_data = []

        self.sample_width = 2

    def run(self):

        print(
            "\n[AUDIO] Starting microphone..."
        )

        try:

            self.audio = pyaudio.PyAudio()


            self.stream = self.audio.open(

                format=pyaudio.paInt16,

                channels=AUDIO_CHANNELS,

                rate=AUDIO_RATE,

                input=True,

                frames_per_buffer=AUDIO_CHUNK
            )

            self.sample_width = (
                self.audio.get_sample_size(
                    pyaudio.paInt16
                )
            )

        except Exception as error:

            print(
                "[AUDIO] ERROR:",
                error
            )

            stop_event.set()

            return

        print(
            "[AUDIO] Optimization started."
        )

        while not stop_event.is_set():

            start_time = time.perf_counter()

            try:


                data = self.stream.read(
                    AUDIO_CHUNK,
                    exception_on_overflow=False
                )

                end_time = time.perf_counter()

        
                latency = (
                    end_time
                    - start_time
                )

                self.total_latency += latency

                if latency > self.maximum_latency:

                    self.maximum_latency = latency

                self.audio_chunks += 1

                # Save audio data locally
                self.audio_data.append(data)

            except Exception as error:

                print(
                    "[AUDIO] Processing error:",
                    error
                )

                break

        self.close()

    def close(self):

        try:

            if self.stream is not None:

                self.stream.stop_stream()
                self.stream.close()

        except Exception:
            pass

        try:

            if self.audio is not None:

                self.audio.terminate()

        except Exception:
            pass

        self.save_audio()

        print(
            "[AUDIO] Optimization stopped."
        )

    def save_audio(self):

        if not self.audio_data:

            print(
                "[AUDIO] No audio data captured."
            )

            return

        try:

            with wave.open(
                AUDIO_FILE,
                "wb"
            ) as audio_file:

                audio_file.setnchannels(
                    AUDIO_CHANNELS
                )

                audio_file.setsampwidth(
                    self.sample_width
                )

                audio_file.setframerate(
                    AUDIO_RATE
                )

                audio_file.writeframes(
                    b"".join(
                        self.audio_data
                    )
                )

            print(
                f"[AUDIO] Saved locally: "
                f"{AUDIO_FILE}"
            )

        except Exception as error:

            print(
                "[AUDIO] Could not save audio:"
            )

            print(error)

    def get_result(self):

        if self.audio_chunks > 0:

            average_latency = (
                self.total_latency
                / self.audio_chunks
            )

        else:

            average_latency = 0

        return {

            "total_audio_chunks":
                self.audio_chunks,

            "average_audio_buffer_latency":
                round(
                    average_latency,
                    4
                ),

            "maximum_audio_buffer_latency":
                round(
                    self.maximum_latency,
                    4
                )
        }


def save_result_to_firebase(
    db,
    video_result,
    audio_result
):

    if db is None:

        print(
            "\n[FIREBASE] No Firebase connection."
        )

        print(
            "[FIREBASE] Result was NOT uploaded."
        )

        return

    try:

        result = {

            "employee_id":
                EMPLOYEE_ID,

            "task":
                "Day 29 - System Optimization",

            "timestamp":
                datetime.now(
                    timezone.utc
                ),

            "video_optimization": {

                "total_frames":
                    video_result[
                        "total_frames"
                    ],

                "processed_frames":
                    video_result[
                        "processed_frames"
                    ],

                "fps":
                    video_result[
                        "fps"
                    ],

                "average_frame_processing_time":
                    video_result[
                        "average_frame_processing_time"
                    ]
            },

            "audio_optimization": {

                "total_audio_chunks":
                    audio_result[
                        "total_audio_chunks"
                    ],

                "average_audio_buffer_latency":
                    audio_result[
                        "average_audio_buffer_latency"
                    ],

                "maximum_audio_buffer_latency":
                    audio_result[
                        "maximum_audio_buffer_latency"
                    ]
            },

            "optimization_methods": {

                "multithreading":
                    True,

                "reduced_camera_buffer":
                    True,

                "controlled_video_resolution":
                    True,

                "frame_resize_optimization":
                    True,

                "chunked_pcm_audio":
                    True,

                "audio_latency_monitoring":
                    True
            }
        }


        document = db.collection(
            FIREBASE_COLLECTION
        ).document()

        document.set(result)

        print(
            "\n[FIREBASE] SUCCESS!"
        )

        print(
            "[FIREBASE] Data saved to collection:"
        )

        print(
            FIREBASE_COLLECTION
        )

        print(
            "[FIREBASE] Document ID:"
        )

        print(
            document.id
        )

    except Exception as error:

        print(
            "\n[FIREBASE] Save failed:"
        )

        print(error)


def print_final_output(
    video_result,
    audio_result
):

    print("\n")
    print("=" * 60)
    print("DAY 29 - OPTIMIZATION RESULT")
    print("=" * 60)

    print("\nVIDEO OPTIMIZATION")
    print("-" * 40)

    print(
        "Total frames:",
        video_result[
            "total_frames"
        ]
    )

    print(
        "Processed frames:",
        video_result[
            "processed_frames"
        ]
    )

    print(
        "FPS:",
        video_result[
            "fps"
        ]
    )

    print(
        "Average frame processing time:",
        video_result[
            "average_frame_processing_time"
        ],
        "seconds"
    )

    print("\nAUDIO OPTIMIZATION")
    print("-" * 40)

    print(
        "Audio chunks:",
        audio_result[
            "total_audio_chunks"
        ]
    )

    print(
        "Average buffer latency:",
        audio_result[
            "average_audio_buffer_latency"
        ],
        "seconds"
    )

    print(
        "Maximum buffer latency:",
        audio_result[
            "maximum_audio_buffer_latency"
        ],
        "seconds"
    )

    print("\nLOCAL AUDIO FILE")
    print("-" * 40)

    print(
        AUDIO_FILE
    )

    print("\nFIREBASE COLLECTION")
    print("-" * 40)

    print(
        FIREBASE_COLLECTION
    )

    print("\n")
    print("=" * 60)
    print("DAY 29 COMPLETED")
    print("=" * 60)


def main():

    print("\n")
    print("=" * 60)
    print("DAY 29 - LOCAL SYSTEM OPTIMIZATION")
    print("=" * 60)

    print(
        "Employee ID:",
        EMPLOYEE_ID
    )

    print(
        "Video + Audio optimization"
    )

    print(
        "Video and Audio will run simultaneously."
    )

    print("=" * 60)


    firebase_db = initialize_firebase()


    video = VideoOptimizer()

    audio = AudioOptimizer()

    video_thread = threading.Thread(
        target=video.run,
        name="VideoOptimizationThread"
    )

    audio_thread = threading.Thread(
        target=audio.run,
        name="AudioOptimizationThread"
    )


    video_thread.start()

    audio_thread.start()


    try:

        while (
            video_thread.is_alive()
            or audio_thread.is_alive()
        ):

            time.sleep(0.5)

    except KeyboardInterrupt:

        print(
            "\n[MAIN] Stopping..."
        )

        stop_event.set()


    stop_event.set()

    video_thread.join()

    audio_thread.join()


    video_result = video.get_result()

    audio_result = audio.get_result()


    print_final_output(
        video_result,
        audio_result
    )


    save_result_to_firebase(
        firebase_db,
        video_result,
        audio_result
    )

if __name__ == "__main__":

    main()