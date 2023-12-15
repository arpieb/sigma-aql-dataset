import glob
import os
import logging
from collections import Counter
import hashlib
import copy

from sigma.collection import SigmaCollection
from sigma.backends.QRadarAQL import QRadarAQLBackend
from sigma.pipelines.QRadarAQL import QRadarAQL_fields_pipeline, QRadarAQL_payload_pipeline
import yaml
from tqdm import tqdm


DATA_DIR = '/Users/rbates/data/aql-sigma'
DATA_DIR_AQL = os.path.join(DATA_DIR, 'aql')
DATA_DIR_SIGMA = os.path.join(DATA_DIR, 'sigma')
SUCCESS = 'success'
FAILED = 'failed'

os.makedirs(DATA_DIR_AQL, exist_ok=True)
os.makedirs(DATA_DIR_SIGMA, exist_ok=True)

pipeline = QRadarAQL_fields_pipeline
backend = QRadarAQLBackend(pipeline())

failures = []
successes = []

# Locate all sigma yaml
path = '../**/*.yml'
for file in tqdm(glob.glob(path, recursive=True)):
    if file.startswith('../rules'):
        try:
            with open(file) as ifs:
                sigma_rules = SigmaCollection.from_yaml(ifs)
            aqls = backend.convert(copy.deepcopy(sigma_rules))
            if len(sigma_rules) == len(aqls):
                for sigma_rule, aql in zip(sigma_rules, aqls):
                    try:
                        sigma = yaml.dump(sigma_rule.to_dict())
                        sha = hashlib.sha256(sigma.encode('utf-8')).hexdigest()
                        with open(os.path.join(DATA_DIR_AQL, f'{sha}.txt'), 'w') as aqlfs:
                            aqlfs.write(aql)
                        with open(os.path.join(DATA_DIR_SIGMA, f'{sha}.txt'), 'w') as sigmafs:
                            sigmafs.write(sigma)
                    except Exception as e:
                        failures.append(f'file: {file}, rule: {sigma_rule.title}, exception: {str(e)}')
                        continue
                successes.append(file)
            else:
                failures.append(f'file: {file}, error: unequal lists, aql={len(aqls)}, sigma={len(sigma_rules)}')
        except Exception as e:
            failures.append(f'file: {file}, exception: {str(e)}')

failed = len(failures)
succeed = len(successes)
print(f'failed: {failed}, succeed: {succeed}')
