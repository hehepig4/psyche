# Setup Instructions

## API Configuration

Before running the code, you need to configure the API settings:

1. **For classification module** (`classify/config.py`):
   - Set `API_KEY` to your API key
   - Set `BASE_URL` to your API base URL

2. **For CAPO module** (`apo/utils.py`):
   - Set `API_KEY` to your API key
   - Set `BASE_URL` to your API base URL

## Running the Code

### Classification Pipeline
```bash
cd classify
python anot.py
python merge.py
# Then run statistics.ipynb for analysis
```

### CAPO Pipeline
```bash
cd apo
python main.py  # Run CAPO process
# Use draw.ipynb for visualization
```

## Note
- The code uses relative paths for maximum portability
- Make sure to install required dependencies before running
