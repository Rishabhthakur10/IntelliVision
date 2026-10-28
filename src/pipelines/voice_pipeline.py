import io
import numpy as np
import streamlit as st

_VOICE_MODULES_AVAILABLE = False
try:
    from resemblyzer import VoiceEncoder, preprocess_wav
    import librosa
    _VOICE_MODULES_AVAILABLE = True
except Exception:
    _VOICE_MODULES_AVAILABLE = False


def is_voice_available() -> bool:
    return _VOICE_MODULES_AVAILABLE


@st.cache_resource
def load_voice_encoder():
    if not _VOICE_MODULES_AVAILABLE:
        return None
    try:
        from resemblyzer import VoiceEncoder
        return VoiceEncoder()
    except Exception:
        return None


def get_voice_embedding(audio_bytes):
    if not _VOICE_MODULES_AVAILABLE or not audio_bytes:
        return None
    try:
        from resemblyzer import preprocess_wav
        import librosa

        encoder = load_voice_encoder()
        if encoder is None:
            return None

        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        wav = preprocess_wav(audio)
        embedding = encoder.embed_utterance(wav)
        return embedding.tolist()
    except Exception as e:
        print(f"Voice embedding error: {e}")
        return None


def identify_speaker(new_embedding, candidates_dict, threshold=0.65):
    if new_embedding is None or not candidates_dict:
        return None, 0.0

    best_sid = None
    best_score = -1.0

    for sid, stored_embedding in candidates_dict.items():
        if stored_embedding:
            similarity = float(np.dot(new_embedding, stored_embedding))
            if similarity > best_score:
                best_score = similarity
                best_sid = sid

    if best_score >= threshold:
        return best_sid, best_score

    return None, best_score


def process_bulk_audio(audio_bytes, candidates_dict, threshold=0.65):
    if not _VOICE_MODULES_AVAILABLE or not audio_bytes:
        return {}

    try:
        encoder = load_voice_encoder()
        if encoder is None:
            return {}

        import librosa
        from resemblyzer import preprocess_wav

        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        wav = preprocess_wav(audio)
        embedding = encoder.embed_utterance(wav)

        detected_scores = {}
        for sid, stored_emb in candidates_dict.items():
            if stored_emb:
                similarity = float(np.dot(embedding, stored_emb))
                if similarity >= threshold:
                    detected_scores[sid] = round(similarity, 3)

        return detected_scores
    except Exception as e:
        print(f"Bulk voice processing error: {e}")
        return {}
