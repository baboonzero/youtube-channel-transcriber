# Remote GPU Testing Guide

## Quick Start (Total time: ~15 minutes)

### 1. Rent GPU on Vast.ai

1. Go to: https://vast.ai/console/create/
2. **Recommended instance:**
   - **GPU:** RTX 4090 or A100
   - **Template:** PyTorch (pre-configured with CUDA)
   - **Storage:** 50GB+
3. Click "Rent" and wait for instance to start (~30 seconds)
4. Copy the SSH command shown (looks like: `ssh -p 12345 root@123.45.67.89`)

### 2. Setup Instance

```bash
# SSH into your instance (use the command from Vast.ai)
ssh -p <PORT> root@<IP>

# Quick setup commands
apt-get update && apt-get install -y ffmpeg
pip install faster-whisper yt-dlp

# Test GPU
nvidia-smi
python3 -c "from faster_whisper import WhisperModel; import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
```

### 3. Transfer Your Code (from your Windows PC)

```cmd
# From your Windows machine, run:
cd "C:\Users\anshu\Downloads\AI Projects\YT Transcribe\scripts"

# Replace <IP> and <PORT> with your instance details
scripts\transfer_to_remote.bat <IP> <PORT>

# Example:
# scripts\transfer_to_remote.bat 123.45.67.89 12345
```

### 4. Run Transcription

```bash
# Back in the SSH session:
cd ~/youtube-transcriber/scripts
python3 run_transcriber.py
```

### 5. Monitor Progress

```bash
# Watch in real-time
tail -f ~/youtube-transcriber/data/transcription.log

# Check current status
python3 -c "
import sqlite3
conn = sqlite3.connect('../data/transcription_progress.db')
cursor = conn.cursor()
cursor.execute('SELECT status, COUNT(*) FROM videos GROUP BY status')
for row in cursor.fetchall():
    print(f'{row[0]}: {row[1]}')
"
```

## Expected Performance

| GPU | Speed vs Your RTX 4060 | Cost/hr | 1000hrs Processing Time |
|-----|------------------------|---------|-------------------------|
| RTX 4060 (yours) | 1x (40x realtime) | Free | ~25 hours |
| RTX 4090 | 2-3x (80-120x) | $0.40 | ~8-12 hours |
| A100 40GB | 4x (160x realtime) | $0.80 | ~6 hours |
| A100 80GB | 4-5x (180x realtime) | $1.50 | ~5.5 hours |

## Cost Estimate for Your Channel

**My First Million (750 videos, ~500 hours):**
- RTX 4090: 8 hours × $0.40 = **$3.20**
- A100: 5 hours × $0.80 = **$4.00**

## Downloading Results

```bash
# After transcription completes, download from Windows:
scp -P <PORT> -r root@<IP>:~/youtube-transcriber/data/transcripts "C:\Users\anshu\Downloads\AI Projects\YT Transcribe\data\"
```

## Tips

1. **Use Interruptible/Spot instances** - 50% cheaper, perfect for this workload
2. **Start small** - Test with 10 videos first to verify everything works
3. **Monitor costs** - Vast.ai shows running cost in real-time
4. **Don't forget to stop** - Destroy instance when done to stop billing

## Troubleshooting

**SSH connection refused:**
- Instance may still be starting, wait 30 seconds

**Out of disk space:**
- Increase storage in Vast.ai instance settings
- Or enable `DELETE_AUDIO_AFTER_TRANSCRIPTION = True` in config.py

**Slow downloads:**
- Choose instance with high DLPerf score (>70)
- Some regions have better YouTube connectivity

## Alternative: RunPod

If Vast.ai is confusing, try RunPod:
1. https://runpod.io
2. Deploy "PyTorch" template
3. Choose A100 or 4090
4. Similar setup process, slightly more expensive
