import os
import wave
import numpy as np
import soundfile as sf

class AudioFormatHandler:
    """Simplified handler for WAV and FLAC only"""
    
    def __init__(self):
        self.supported_formats = ['wav', 'flac']
    
    def detect_format(self, file_path):
        """Detect and validate WAV or FLAC files"""
        try:
            if not os.path.exists(file_path):
                return {'error': 'File not found'}
            
            ext = os.path.splitext(file_path)[1].lower().lstrip('.')
            
            if ext not in self.supported_formats:
                return {'error': f'Unsupported format: {ext}. Only WAV and FLAC supported.'}
            
            format_info = {
                'file_path': file_path,
                'format': ext,
                'is_lossless': True,
                'supports_lsb': True,
                'steganography_method': 'lsb',
                'size_mb': os.path.getsize(file_path) / (1024 * 1024)
            }
            
            if ext == 'wav':
                return self._analyze_wav(file_path, format_info)
            else:  # flac
                return self._analyze_flac(file_path, format_info)
                
        except Exception as e:
            return {'error': f'Format detection failed: {str(e)}'}
    
    def _analyze_wav(self, file_path, format_info):
        """Analyze WAV file"""
        try:
            with wave.open(file_path, 'rb') as wav_file:
                if wav_file.getsampwidth() != 2:
                    return {'error': 'WAV file must be 16-bit PCM'}
                
                format_info.update({
                    'codec': 'PCM',
                    'sample_rate': wav_file.getframerate(),
                    'channels': wav_file.getnchannels(),
                    'duration': wav_file.getnframes() / wav_file.getframerate(),
                    'bit_depth': wav_file.getsampwidth() * 8
                })
            return format_info
        except Exception as e:
            return {'error': f'WAV analysis failed: {str(e)}'}
    
    def _analyze_flac(self, file_path, format_info):
        """Analyze FLAC file"""
        try:
            info = sf.info(file_path)
            format_info.update({
                'codec': 'FLAC',
                'sample_rate': info.samplerate,
                'channels': info.channels,
                'duration': info.duration,
                'bit_depth': 16  # We'll convert to 16-bit
            })
            return format_info
        except Exception as e:
            return {'error': f'FLAC analysis failed: {str(e)}'}
    
    def to_pcm(self, file_path, format_info):
        """Convert audio to writable 16-bit PCM numpy array"""
        try:
            if format_info['format'] == 'wav':
                with wave.open(file_path, 'rb') as wav_file:
                    frames = wav_file.readframes(wav_file.getnframes())
                    pcm_data = np.frombuffer(frames, dtype=np.int16)
                    return pcm_data.copy()  # Ensure writable
            
            else:  # flac
                audio_data, sample_rate = sf.read(file_path, dtype='int16')
                if len(audio_data.shape) > 1:  # Multi-channel
                    pcm_data = audio_data.flatten()
                else:
                    pcm_data = audio_data
                return pcm_data.copy()  # Ensure writable
                
        except Exception as e:
            raise ValueError(f"PCM conversion failed: {str(e)}")
    
    def from_pcm(self, pcm_data, output_path, format_info):
        """Convert PCM back to original format"""
        try:
            if format_info['format'] == 'wav':
                with wave.open(output_path, 'wb') as wav_file:
                    wav_file.setnchannels(format_info['channels'])
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(format_info['sample_rate'])
                    wav_file.writeframes(pcm_data.astype(np.int16).tobytes())
            
            else:  # flac
                if format_info['channels'] > 1:
                    # Reshape for multi-channel
                    audio_data = pcm_data.reshape(-1, format_info['channels'])
                else:
                    audio_data = pcm_data.reshape(-1, 1)
                
                sf.write(output_path, audio_data, format_info['sample_rate'], 
                        format='FLAC', subtype='PCM_16')
                
        except Exception as e:
            raise ValueError(f"Format conversion failed: {str(e)}")
    
    def estimate_capacity(self, format_info, data_size_bytes):
        """Estimate storage capacity"""
        total_samples = int(format_info['sample_rate'] * format_info['duration'] * format_info['channels'])
        available_bits = total_samples - 32  # 32 bits for length header
        required_bits = data_size_bytes * 8
        
        return {
            'can_hold': available_bits >= required_bits,
            'available_bits': available_bits,
            'required_bits': required_bits,
            'capacity_percentage': (required_bits / available_bits * 100) if available_bits > 0 else 0,
            'method': 'LSB'
        }
