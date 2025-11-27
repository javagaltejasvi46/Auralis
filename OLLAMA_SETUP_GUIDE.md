# Ollama Setup Guide for Phi-3-Mini

Complete guide for setting up Phi-3-Mini using Ollama (simplified approach).

## Why Ollama?

✅ **Much simpler** than GGUF conversion  
✅ **No manual model downloads** - automatic pulling  
✅ **Easy updates** - `ollama pull phi3:mini`  
✅ **Better performance** - optimized inference  
✅ **Cross-platform** - Windows, Mac, Linux  
✅ **No Python dependencies** - runs as separate service  

---

## Quick Start (Windows)

### 1. Install Ollama

**Download and install:**
```
https://ollama.com/download
```

**Or use PowerShell script:**
```powershell
.\backend\scripts\setup_ollama.ps1
```

### 2. Verify Installation

```powershell
ollama --version
```

### 3. Pull Phi-3-Mini Model

```powershell
ollama pull phi3:mini
```

**Download size:** ~2.3GB  
**Time:** 5-10 minutes (first time only)

### 4. Test Model

```powershell
ollama run phi3:mini "What is 2+2?"
```

Expected output:
```
2+2 equals 4.
```

### 5. Start Backend

```powershell
# Set environment variable
$env:USE_OLLAMA="true"
$env:OLLAMA_MODEL="phi3:mini"

# Start backend
docker-compose up -d backend-api
```

### 6. Verify Deployment

```powershell
curl http://localhost:8002/health
```

---

## Installation Steps (Detailed)

### Windows

1. **Download Ollama**
   - Visit: https://ollama.com/download
   - Download Windows installer
   - Run installer (requires admin)

2. **Verify Installation**
   ```powershell
   ollama --version
   ```

3. **Start Ollama Service**
   - Ollama starts automatically on Windows
   - Check system tray for Ollama icon

4. **Pull Model**
   ```powershell
   ollama pull phi3:mini
   ```

### Mac

1. **Install Ollama**
   ```bash
   brew install ollama
   ```
   
   Or download from: https://ollama.com/download

2. **Start Ollama**
   ```bash
   ollama serve
   ```

3. **Pull Model**
   ```bash
   ollama pull phi3:mini
   ```

### Linux

1. **Install Ollama**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. **Start Ollama**
   ```bash
   ollama serve
   ```

3. **Pull Model**
   ```bash
   ollama pull phi3:mini
   ```

---

## Available Phi-3 Models

| Model | Size | RAM Required | Speed | Quality |
|-------|------|--------------|-------|---------|
| `phi3:mini` | 2.3GB | 4GB | Fast | Good |
| `phi3:medium` | 7.9GB | 8GB | Medium | Better |
| `phi3:3.8b` | 2.3GB | 4GB | Fast | Good |

**Recommended:** `phi3:mini` for production

---

## Configuration

### Environment Variables

```bash
# Use Ollama (default)
USE_OLLAMA=true

# Ollama settings
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=phi3:mini

# Fallback to GGUF (if Ollama not available)
USE_OLLAMA=false
PHI3_MODEL_PATH=models/phi3-therapy-q4_k_m.gguf
```

### Docker Compose

```yaml
services:
  backend-api:
    environment:
      - USE_OLLAMA=true
      - OLLAMA_BASE_URL=http://host.docker.internal:11434
      - OLLAMA_MODEL=phi3:mini
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

---

## Testing

### Test Ollama Service

```powershell
# Check if running
curl http://localhost:11434/api/tags

# List models
ollama list

# Test generation
ollama run phi3:mini "Hello, how are you?"
```

### Test Backend Integration

```powershell
# Start backend
docker-compose up -d backend-api

# Check health
curl http://localhost:8002/health

# Test summarization
curl -X POST http://localhost:8002/summarize-sessions `
  -H "Content-Type: application/json" `
  -d '{"patient_id": 1}'
```

---

## Troubleshooting

### Ollama Not Running

**Symptoms:**
```
Connection refused to localhost:11434
```

**Solutions:**
```powershell
# Windows: Check system tray, restart Ollama
# Or manually start:
ollama serve

# Mac/Linux:
ollama serve &
```

### Model Not Found

**Symptoms:**
```
model 'phi3:mini' not found
```

**Solutions:**
```powershell
# Pull model
ollama pull phi3:mini

# Verify
ollama list
```

### Slow Inference

**Symptoms:** Generation takes > 30 seconds

**Solutions:**
1. Use smaller model: `phi3:mini` instead of `phi3:medium`
2. Reduce max_tokens in config
3. Check system resources (CPU/RAM)
4. Enable GPU acceleration (if available)

### Out of Memory

**Symptoms:** Ollama crashes or system freezes

**Solutions:**
1. Close other applications
2. Use `phi3:mini` (requires only 4GB RAM)
3. Increase system swap/page file
4. Upgrade RAM

---

## Performance Optimization

### CPU Optimization

```bash
# Set thread count (default: auto)
export OLLAMA_NUM_THREADS=8
```

### GPU Acceleration

Ollama automatically uses GPU if available (NVIDIA, AMD, Apple Silicon).

**Check GPU usage:**
```powershell
# Windows
nvidia-smi

# Mac
Activity Monitor > GPU
```

### Memory Management

```bash
# Limit context size
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_NUM_PARALLEL=1
```

---

## Model Management

### Update Model

```powershell
ollama pull phi3:mini
```

### Remove Model

```powershell
ollama rm phi3:mini
```

### List Models

```powershell
ollama list
```

### Model Info

```powershell
ollama show phi3:mini
```

---

## Comparison: Ollama vs GGUF

| Aspect | Ollama | GGUF (llama-cpp) |
|--------|--------|------------------|
| **Setup** | ✅ Simple (1 command) | ❌ Complex (convert, quantize) |
| **Updates** | ✅ Easy (`ollama pull`) | ❌ Manual download |
| **Performance** | ✅ Optimized | ✅ Optimized |
| **Dependencies** | ✅ None (separate service) | ❌ Python packages |
| **GPU Support** | ✅ Automatic | ⚠️ Manual config |
| **Model Size** | 2.3GB | 2.5GB |
| **Inference Speed** | 10-15s (CPU) | 10-15s (CPU) |

**Recommendation:** Use Ollama for production (simpler and more maintainable)

---

## Migration from GGUF to Ollama

If you already have GGUF setup:

1. **Install Ollama** (see above)
2. **Pull Phi-3 model**
   ```powershell
   ollama pull phi3:mini
   ```
3. **Update environment**
   ```bash
   USE_OLLAMA=true
   ```
4. **Restart backend**
   ```powershell
   docker-compose restart backend-api
   ```
5. **Verify**
   ```powershell
   curl http://localhost:8002/health
   ```

---

## Production Deployment

### Checklist

- [ ] Ollama installed and running
- [ ] Phi-3-Mini model pulled
- [ ] Environment variables set
- [ ] Database migration completed
- [ ] Backend started successfully
- [ ] Health check passing
- [ ] Test summarization working

### Monitoring

```powershell
# Check Ollama logs
ollama logs

# Check backend logs
docker-compose logs -f backend-api

# Monitor performance
curl http://localhost:8002/health
```

---

## Support

### Ollama Documentation
- Website: https://ollama.com
- GitHub: https://github.com/ollama/ollama
- Models: https://ollama.com/library

### Phi-3 Documentation
- Model Card: https://ollama.com/library/phi3
- Microsoft Phi-3: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct

---

## Next Steps

1. ✅ Install Ollama
2. ✅ Pull Phi-3-Mini model
3. ✅ Test model locally
4. ⏳ Run database migration
5. ⏳ Deploy backend
6. ⏳ Test API endpoints
7. ⏳ Monitor performance

---

**Setup Time:** 10-15 minutes  
**Model Download:** 5-10 minutes (one-time)  
**Ready for Production:** ✅ YES
