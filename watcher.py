from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from os import path, walk, remove
import PyStatGen as pst


tkp = pst.Task.with_details
token = "launch_token"


class SourceEventHandler(FileSystemEventHandler):
    def __init__(self, tasker):
        self.tasker = tasker
        self.content = list()

    def on_created(self, event):
        if path.split(event.src_path)[1] == token and not event.is_directory:
            # Assing configuration shortcuts
            tp = self.tasker.conf.get("templates")
            ta = self.tasker.conf.get("target")
            sc = self.tasker.conf.get("source")
            # Check for errors
            (stop, error_message) = pst.test_match(self.tasker.conf)
            if stop:
                pst.notify(path.join(sc, "errors.txt"), error_message)
                pst.notify_stdout(error_message)
                remove(event.src_path)
                return

            # Tasks~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # Folder structure tasks
            default_tasks = list()
            check_list = [ta, path.join(ta, "css"), path.join(ta, "fonts"),
                          path.join(ta, "css", "default-skin"),
                          path.join(ta, "img"), path.join(ta, "img", "full"),
                          path.join(ta, "img", "thumb"), path.join(ta, "js")]
            for directory in check_list:
                try:
                    pst.test_writability(directory)
                except pst.FileError as e:
                    default_tasks.append(tkp(pst.FileTypes.directory,
                                             pst.TaskTypes.generate,
                                             {"path": e.path}))
            # Default folder content tasks
            for folder in ["css", "img", "fonts", "js"]:
                for d in walk(path.join(tp, folder)):
                    for f in d[2]:
                        src = path.join(d[0], f)
                        dst = path.join(d[0].replace(tp, ta), f)
                        pst.test_readability(dst)
                        tk = tkp(pst.FileTypes.misc,
                                 pst.TaskTypes.copy,
                                 {"src": src, "dst": dst})
                        default_tasks.append(tk)
            pst.test_readability(path.join(ta, "img/background.jpg"))
            copy_info = {"src": path.join(sc, "background.jpg"),
                         "dst": path.join(ta, "img/background.jpg")}
            default_tasks.append(tkp(pst.FileTypes.image,
                                     pst.TaskTypes.copy,
                                     copy_info))
            pst.test_readability(path.join(ta, "img/share.png"))
            copy_info = {"src": path.join(sc, "share.png"),
                         "dst": path.join(ta, "img/share.png")}
            default_tasks.append(tkp(pst.FileTypes.image,
                                     pst.TaskTypes.copy,
                                     copy_info))
            # Website content tasks
            new_content = self.tasker.read_content()
            self.tasker.build_tasks(new_content, self.content)

            # Generate website
            pst.process(self.tasker.conf, default_tasks + self.tasker.tasks)

            # Synchronize
            pst.git_sync(self.tasker.conf, default_tasks + self.tasker.tasks)

            pst.notify(path.join(sc, "results.txt"),
                       pst.now_str() + " Generated the website succesfully.")
            # Cleanup
            self.content = new_content
            self.tasker.tasks.clear()
            remove(event.src_path)


class Watcher:
    ''' Folder watcher that triggers appropriate generation events. '''

    def __init__(self, tasker, get_default_tasks=None):
        self.tasker = tasker
        self.src_observer = Observer()

    def start(self):
        event_handler = SourceEventHandler(self.tasker)
        self.src_observer.schedule(event_handler,
                                   self.tasker.conf.get("source"),
                                   recursive=True)
        self.src_observer.start()

    def stop(self):
        self.src_observer.stop()

    def join(self):
        self.src_observer.join()
