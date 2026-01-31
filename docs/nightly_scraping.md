# Script for Running Safe Nightly Scraping

## Robust Scraper Features

✅ **Checkpoint System**
- Saves progress every 50 points
- Can be interrupted and resumed
- No data loss on failure

✅ **Automatic Retries**
- 3 silver attempts per point
- Incremental wait (5s, 10s, 15s)
- Continues even if some points fail

✅ **Detailed Logging**
- Log file with timestamp
- Progress updates every 10 points
- Speed and remaining time estimated

✅ **Automatic Recovery**
- Saves progress if interrupted
- Run again to continue from where it left off
- Cleans up checkpoints upon completion

---

## How to Run

### Step 1: Activate virtual environment
```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 2: Run scraper
```powershell
python scripts\scrape_2017_robusto.py
```

### Step 3: Let it run
- Minimize the window
- Leave the PC on
- Go to sleep 😴

---

## Monitoring (Optional)

If you want to see progress without opening the window:

```powershell
# See the last 20 lines of the log
Get-Content logs\scrape_2017_*.log -Tail 20 -Wait
```

---

## If Something Goes Wrong

### Case 1: Scraping is interrupted
```powershell
# Simply run it again
python scripts\scrape_2017_robusto.py

# Automatically continues from where it left off
```

### Case 2: You want to pause manually
```
Ctrl + C in the terminal

# To resume:
python scripts\scrape_2017_robusto.py
```

### Case 3: Verify progress
```powershell
# See current checkpoint
Get-Content outputs\checkpoint_2017.json
```

---

## Generated Files

During scraping:
- `outputs/checkpoint_2017.json` - Current progress
- `outputs/ano_2017_partial.json` - Partial data
- `logs/scrape_2017_YYYYMMDD_HHMMSS.log` - Detailed log

Upon completion:
- `outputs/ano_2017_completo_con_hash.json` - Final data
- Checkpoints are automatically deleted

---

## Estimates

- **Start**: ~00:10 (whenever you run it)
- **End**: ~05:30 (5.3 hours later)
- **Total points**: 1,460
- **Checkpoints**: 29 (every 50 points)
- **Final size**: ~120 MB

---

## Pre-Scraping Checklist

- [ ] PC connected to power
- [ ] Stable internet
- [ ] Virtual environment activated
- [ ] Sufficient disk space (>500 MB)
- [ ] Sleep settings disabled

### Disable Sleep (Windows)

```powershell
# Prevent the PC from sleeping
powercfg /change standby-timeout-ac 0
powercfg /change monitor-timeout-ac 30
```

---

## After Scraping

Tomorrow when you wake up:

1. **Verify it finished**
   ```powershell
   # See the last 50 lines of the log
   Get-Content logs\scrape_2017_*.log -Tail 50
   ```

2. **Validate data**
   ```powershell
   python scripts\analyze_2017.py
   ```

3. **Upload to Supabase**
   ```powershell
   python scripts\upload_to_supabase.py
   ```

---

## Emergency Contact

If something fails and you need help:
- Check the most recent log in `logs/`
- Check the checkpoint in `outputs/checkpoint_2017.json`
- The scraper can always be resumed

---

## Good luck! 🚀

The scraper is designed to be 100% reliable.
Sleep tight, tomorrow you'll have all the 2017 data.
