# Book Genre Classification (Chitanka)

Multi-label genre classification for Bulgarian literature scraped from [chitanka.info](https://chitanka.info). Implements and compares two approaches: **Complement Naive Bayes** and an **LSTM Recurrent Neural Network**.

## Requirements

```bash
pip install tensorflow pandas numpy matplotlib stop-words
```

## Usage

### 1. Complement Naive Bayes
Custom CNB implementation tailored for class-imbalanced, multi-label Bulgarian text.

```bash
python NaiveBayes/model.py
```
*(Check and update data paths inside `NaiveBayes/model.py` to match your local setup).*

### 2. LSTM Neural Network
Keras Sequential model (`Embedding` → `LSTM` → `Dense(sigmoid)`) with dynamic prediction thresholding.

- **Train:**
  ```bash
  cd RNN
  python buildRNN.py
  ```
- **Evaluate pre-trained weights (`modelK3.h5`):**
  ```bash
  cd RNN
  python loadRNN.py
  ```
  Outputs predictions and matches to `RNN/test_output.txt`.

## Dataset & Analytics

- `data/<id>/text.txt`: Raw text files corresponding to book/story entries.
- `utils/data.json`: Metadata mapping IDs to titles, authors, and genre lists.
- `utils/AI.py`: Plots dataset genre distribution.
- `utils/jsonAnalyze.py`: Analyzes text word counts and length categories.
