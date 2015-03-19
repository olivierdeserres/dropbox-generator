import PyStatGen as pst
import yaml
from os import path, walk
import argparse


def main():
    prs = argparse.ArgumentParser(description='Generate the website anew.')
    prs.add_argument('-c', '--conf', type=str,
                     default="example_configuration.yml", dest='conf_path',
                     help='Path to the configuration file.')
    args = prs.parse_args()

    conf = yaml.load(open(args.conf_path, 'r').read())

    tp = conf.get("templates")
    ta = conf.get("target")
    sc = conf.get("source")

    default_tasks = list()
    # Integrity tasks
    check_list = [ta, path.join(ta, "css"), path.join(ta, "fonts"),
                  path.join(ta, "css", "default-skin"),
                  path.join(ta, "img"), path.join(ta, "img", "full"),
                  path.join(ta, "img", "thumb"), path.join(ta, "js")]
    for directory in check_list:
        try:
            pst.test_writability(directory)
        except pst.FileError as e:
            default_tasks.append(pst.Task.with_details(pst.FileTypes.directory,
                                                       pst.TaskTypes.generate,
                                                       {"path": e.path}))
    # Copy tasks
    for folder in ["css", "img", "fonts", "js"]:
        for d in walk(path.join(tp, folder)):
            for f in d[2]:
                src = path.join(d[0], f)
                dst = path.join(d[0].replace(tp, ta), f)
                try:
                    pst.test_readability(dst)
                except pst.FileError as e:
                    tk = pst.Task.with_details(pst.FileTypes.misc,
                                               pst.TaskTypes.copy,
                                               {"src": src, "dst": dst})
                    default_tasks.append(tk)
    try:
        pst.test_readability(path.join(ta, "img/background.jpg"))
    except pst.FileError as e:
        copy_info = {"src": path.join(sc, "background.jpg"),
                     "dst": path.join(ta, "img/background.jpg")}
        default_tasks.append(pst.Task.with_details(pst.FileTypes.image,
                                                   pst.TaskTypes.copy,
                                                   copy_info))
    try:
        pst.test_readability(path.join(ta, "img/share.png"))
    except pst.FileError as e:
        copy_info = {"src": path.join(sc, "share.png"),
                     "dst": path.join(ta, "img/share.png")}
        default_tasks.append(pst.Task.with_details(pst.FileTypes.image,
                                                   pst.TaskTypes.copy,
                                                   copy_info))

    tasker = pst.Tasker(conf)
    content = tasker.read_content()

    old_content = []

    tasker.build_tasks(content, old_content)
    pst.process(conf, default_tasks + tasker.tasks)

if __name__ == "__main__":
    main()
