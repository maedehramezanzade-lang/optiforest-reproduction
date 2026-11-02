"""Credit Card Fraud (Kaggle: mlg-ulb/creditcardfraud). Download the zip manually from kaggle.com, unzip creditcard.csv,
then:  python src/prepare_creditcard.py --csv creditcard.csv --out data/creditcard.csv
Writes the common format used by the runners: features..., label (1 = fraud), no header."""
import argparse, os, pandas as pd
ap = argparse.ArgumentParser(); ap.add_argument('--csv', default='creditcard.csv'); ap.add_argument('--out', default='data/creditcard.csv')
a = ap.parse_args()
cc = pd.read_csv(a.csv)
print('Shape:', cc.drop(columns=['Class']).shape, '| fraud ratio:', round(cc['Class'].mean(), 5))
os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
pd.concat([cc.drop(columns=['Class']), cc['Class']], axis=1).to_csv(a.out, header=False, index=False)
print('Saved', a.out)
