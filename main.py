import copy
import glob
import hashlib
import logging
import os
import warnings
from collections import Counter

import fire
import yaml
from sigma.backends.QRadarAQL import QRadarAQLBackend
from sigma.collection import SigmaCollection
from sigma.pipelines.QRadarAQL import QRadarAQL_fields_pipeline
from tqdm import tqdm

# Disable warnings being kicked out by pysigma
warnings.filterwarnings("ignore")

# Set up logging
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(open('sigma-aql-dataset.log', 'w'))]
)
logging.getLogger().setLevel(
    logging.getLevelName(
        os.getenv('LOG_LEVEL', 'INFO').upper()
    )
)


def main(sigma_path, dataset_path='dataset', glob_path='**/*.yml'):
    """
    Main converter function
    :param sigma_path: Base path to search for sigma rules
    :param dataset_path: Output pathf or dataset
    :param glob_path: Glob path pattern to match files under sigma_path
    :return: None
    """
    # Define local consts
    FILE_SUCCESS = 'file_success'
    FILE_FAILED = 'file_failed'
    RULE_SUCCESS = 'rule_success'
    RULE_FAILED = 'rule_failed'

    # Ensure all paths exist
    aql_outdir = os.path.join(dataset_path, 'aql')
    os.makedirs(aql_outdir, exist_ok=True)
    sigma_outdir = os.path.join(dataset_path, 'sigma')
    os.makedirs(sigma_outdir, exist_ok=True)

    # Set up converter pipeline and backend
    pipeline = QRadarAQL_fields_pipeline
    backend = QRadarAQLBackend(pipeline())

    # Define metrics
    metrics = Counter({
        FILE_SUCCESS: 0,
        FILE_FAILED: 0,
        RULE_SUCCESS: 0,
        RULE_FAILED: 0,
    })

    # Go find and convert files
    path = os.path.join(sigma_path, glob_path)
    for file in tqdm(glob.glob(path, recursive=True)):
        try:
            with open(file) as ifs:
                sigma_rules = SigmaCollection.from_yaml(ifs)
            aqls = backend.convert(copy.deepcopy(sigma_rules))
            if len(sigma_rules) == len(aqls):
                for sigma_rule, aql in zip(sigma_rules, aqls):
                    try:
                        sigma = yaml.dump(sigma_rule.to_dict())
                        sha = hashlib.sha256(sigma.encode('utf-8')).hexdigest()
                        with open(
                                os.path.join(aql_outdir, f'{sha}.txt'),
                                'w') as aqlfs:
                            aqlfs.write(aql)
                        with open(
                                os.path.join(sigma_outdir, f'{sha}.txt'),
                                'w') as sigmafs:
                            sigmafs.write(sigma)
                        metrics[RULE_SUCCESS] += 1
                    except Exception as e:
                        metrics[RULE_FAILED] += 1
                        logging.error(
                            f'file: {file}, '
                            f'rule: {sigma_rule.title}, '
                            f'exception: {str(e)}')
                        continue
                metrics[FILE_SUCCESS] += 1
            else:
                metrics[FILE_FAILED] += 1
                logging.error(
                    f'file: {file}, '
                    f'error: unequal lists, '
                    f'aql={len(aqls)}, sigma={len(sigma_rules)}')
        except Exception as e:
            metrics[FILE_FAILED] += 1
            logging.error(f'file: {file}, exception: {str(e)}')
            continue

    logging.info(metrics)
    print(metrics)


if __name__ == '__main__':
    fire.Fire(main)
