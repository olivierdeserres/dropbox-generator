import PyStatGen as pst
import yaml
import argparse
import time
from watcher import Watcher


def main():
    prs = argparse.ArgumentParser(description='Generate the website anew.')
    prs.add_argument('-c', '--conf', type=str,
                     default="example_configuration.yml", dest='conf_path',
                     help='Path to the configuration file.')
    args = prs.parse_args()
    conf = yaml.load(open(args.conf_path, 'r').read())
    task_manager = pst.Tasker(conf)
    task_manager.content = task_manager.read_content()
    watcher = Watcher(task_manager)
    watcher.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()
    watcher.join()


if __name__ == "__main__":
    main()
