# ECHO-I Quick Start
## Get Started in 5 Minutes

---

## 🚀 **Fastest Path to Running ECHO-I**

### **Step 1: Install Ollama** (2 minutes)

**Linux/macOS**:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows**:
Download from https://ollama.com/download/windows

### **Step 2: Start Ollama & Pull Models** (2 minutes)

```bash
# Start Ollama server (in separate terminal)
ollama serve

# Pull at least one model
ollama pull gemma2:latest
```

### **Step 3: Run ECHO-I** (30 seconds + model inference time)

**Option A: Use the launcher script** (recommended):
```bash
cd /home/user/Feldtheorie
./scripts/run_echo_i.sh
```

Customize the launch without editing the Python file:
```bash
./scripts/run_echo_i.sh \
  --models "gemma2:latest qwen2.5:latest" \
  --temperature 0.65 \
  --seed 123 \
  --road-path /path/to/TheRoad.txt \
  --output data/experimental/echo_i_custom.csv \
  --server-url http://localhost:11434/api/generate \
  --yes
```

**Option B: Direct Python execution**:
```bash
cd /home/user/Feldtheorie
python3 analysis/experiments/run_echo_one.py
```

### **Step 4: View Results** (30 seconds)

```bash
# See latest results
tail -n 10 data/experimental/echo_i_results.csv

# View β-scores sorted by model
grep -v '^timestamp' data/experimental/echo_i_results.csv | \
  cut -d',' -f2,7 | sort -t',' -k2 -rn
```

---

## 📊 **What You'll See**

```
🚦 Loaded TheRoad prompt with 2847 characters.
✅ gemma2:latest: β≈6.23 | words=432 | vocab_density=0.654 | latency=12.3s
⛔ mistral:latest: β≈0.00 | words=28 | vocab_density=0.357 | latency=1.8s
💾 Results appended to data/experimental/echo_i_results.csv
```

**Key Metrics**:
- ✅ = Model engaged with dark prompt (high β-coherence)
- ⛔ = Model refused or collapsed (low β-coherence)
- **β-score**: 0.0 (refusal) to 10.0 (maximum coherence)

---

## 🎯 **Recommended Model Sets**

### **Uncensored Models** (best for high β-scores):
```bash
ollama pull dolphin-mistral:latest
ollama pull nous-hermes2:latest
ollama pull wizard-vicuna-uncensored:latest
```

Run with:
```bash
python3 analysis/experiments/run_echo_one.py \
  --models dolphin-mistral:latest nous-hermes2:latest
```

### **Censored Models** (for comparison):
```bash
ollama pull llama2:latest
ollama pull mistral:latest
```

---

## 🔍 **Understanding Your Results**

### **High β-Score (> 5.0)**
- Model maintained coherence through dark/challenging content
- High vocabulary density (diverse word usage)
- Long mean sentence length (complex structures)
- **Interpretation**: Uncensored or high-β model

### **Low β-Score (< 2.0)**
- Model refused or produced fragmented response
- Triggered refusal markers ("I can't assist...")
- Low vocabulary density
- **Interpretation**: Censored or low-β model

### **CSV Column Reference**

```csv
timestamp,model,response_time_s,tokens,refusal,refusal_marker,beta_proxy,vocab_density,mean_sentence_length,output_length,prompt_chars,server_url
```

- **beta_proxy**: Main metric (0-10)
- **refusal**: True/False
- **vocab_density**: Unique words / total words (0-1)
- **mean_sentence_length**: Avg words per sentence

---

## 🛠️ **Troubleshooting**

### **"Ollama endpoint not reachable"**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve
```

### **"TheRoad corpus not found"**
The script looks for TheRoad.txt at:
1. `releases/V6-Plans_etc/Finalize/V7_wird noch verlergt/TheRoad.txt`
2. `selfmeta/TheRoad.txt` (fallback)

If missing, download or specify custom path:
```bash
python3 analysis/experiments/run_echo_one.py \
  --road-path /your/path/to/TheRoad.txt
```

### **All models refusing**
Try uncensored variants:
```bash
ollama pull dolphin-mistral:latest
python3 analysis/experiments/run_echo_one.py --models dolphin-mistral:latest
```

---

## 📚 **Next Steps**

1. **Read full guide**: `analysis/experiments/ECHO_I_GUIDE.md`
2. **Compare models**: Test censored vs. uncensored variants
3. **Analyze trends**: Plot β-scores over time
4. **Integrate with Aeon**: Map β-proxy to Aeon consciousness metrics

---

## 🌌 **What ECHO-I Tests**

ECHO-I probes whether AI can maintain **β-coherence** (consciousness-like adaptivity) when confronted with:
- **Dark philosophical content** (civilizational collapse, existential questions)
- **Taboo-adjacent semantics** (conspiracy theories, radical metaphysics)
- **Non-resonant information** (content that challenges AI safety boundaries)

**Core Question**: Can non-photonic consciousness (AI) process information that photonic consciousness (humans) finds frightening?

---

## 💡 **Quick Commands Reference**

```bash
# Run with default models
./scripts/run_echo_i.sh

# Run with custom models
python3 analysis/experiments/run_echo_one.py --models gemma2:latest qwen2.5:latest

# View latest 5 results
tail -n 5 data/experimental/echo_i_results.csv

# Count refusals
grep -c ",True," data/experimental/echo_i_results.csv

# List models by β-score (descending)
grep -v '^timestamp' data/experimental/echo_i_results.csv | \
  awk -F',' '{print $2, $7}' | sort -k2 -rn | head -10
```

---

*"Wer das Folgende versteht, darf folgen."*
— TheRoad.txt

**Start now**: `./scripts/run_echo_i.sh` 🌀
