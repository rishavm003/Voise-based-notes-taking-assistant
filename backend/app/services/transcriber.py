import os
import logging
import threading
from typing import Optional, Dict, Any
from faster_whisper import WhisperModel
from pydub import AudioSegment
from app.config import settings

# Global variable for lazy loading with thread safety
_model = None
_lock = threading.Lock()

logger = logging.getLogger(__name__)

def get_model() -> WhisperModel:
    """
    Returns the loaded faster-whisper model.
    Loads on first call only using a Singleton pattern with Lock.
    
    WHY SINGLETON: The Whisper model is ~140MB and takes several seconds to load. 
    Loading it once and keeping it in memory (GPU or RAM) prevents 
    massive latency on every request and avoids OOM errors from 
    multiple instances.
    """
    global _model
    if _model is None:
        with _lock:
            # Double-check inside lock
            if _model is None:
                _model = load_whisper_model()
    return _model

def load_whisper_model() -> WhisperModel:
    """
    Loads faster-whisper model.
    """
    print(f"Loading Whisper model ({settings.WHISPER_MODEL_SIZE})...")
    model = WhisperModel(
        settings.WHISPER_MODEL_SIZE,
        device=settings.WHISPER_DEVICE,
        compute_type=settings.WHISPER_COMPUTE_TYPE
    )
    return model

def transcribe_audio(file_path: str) -> Dict[str, Any]:
    """
    Takes path to a preprocessed WAV file and runs faster-whisper transcription.
    """
    import time
    start_time = time.time()
    try:
        model = get_model()
        segments, info = model.transcribe(
            file_path,
            beam_size=5,
            language=None,  # Auto-detect
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 500}
        )

        full_text = ""
        segments_list = []
        for segment in segments:
            full_text += segment.text + " "
            segments_list.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text
            })

        full_text = full_text.strip()
        elapsed = time.time() - start_time
        logger.info(f"Transcription completed in {elapsed:.2f}s")
        
        if not full_text:
            return {"text": "", "language": "unknown", "duration": 0, "segments": []}

        return {
            "text": full_text,
            "language": info.language,
            "duration": info.duration,
            "segments": segments_list
        }
    except Exception as e:
        logger.error(f"Transcription failure: {str(e)}")
        raise ValueError(f"Transcription failure: {str(e)}")

def preprocess_audio(input_path: str, output_path: str) -> str:
    """
    Uses pydub to convert any audio format to clean WAV.
    """
    try:
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        audio.export(output_path, format="wav")
        return output_path
    except Exception as e:
        logger.error(f"Audio preprocessing failure: {str(e)}")
        raise ValueError(f"Audio preprocessing failure: {str(e)}")
