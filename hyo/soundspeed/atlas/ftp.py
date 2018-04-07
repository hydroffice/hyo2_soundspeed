import ftplib
import socket

import sys
import os

import logging

log = logging.getLogger(__name__)


class ProgressBar:
    """ Class used to store the options of a progress bar """

    def __init__(self, start_state=0.0, end_state=10.0, bar_width=12, bar_fill='+', bar_blank='-',
                 bar_format='[%(fill)s@%(blank)s] %(progress)s%%', use_stdout=sys.stdout):
        """ Initialize the progress bar

        Args:
            start_state:   state from which start the progress
            end_state:     state in which the progress has terminated.
            bar_width:     width of the progress bar
            bar_fill:      char used for downloaded data chunks
            bar_blank:     char used for remaining space
            bar_format:    format settings for the progress bar
            use_stdout:    file-object to which send the progress status (default, use sys.stdout)
        """

        self.start = start_state
        self.end = end_state
        self.width = bar_width
        self.fill = bar_fill
        self.blank = bar_blank
        self.bar_format = bar_format
        self.stdout = use_stdout
        self.progress = 0.0
        self.reset()

    def add(self, increment):
        if self.end > (self.progress + increment):
            self.progress += increment
        else:
            self.progress = float(self.end)

    def sub(self, decrement):
        if self.start < self.progress - decrement:
            self.progress -= decrement
        else:
            self.progress = float(self.start)

    def __repr__(self):
        cur_width = int(self.progress / self.end * self.width)
        fill = cur_width * self.fill
        blank = (self.width - cur_width) * self.blank
        percentage = int(self.progress / self.end * 100)
        return self.bar_format % {'fill': fill, 'blank': blank, 'progress': percentage}

    def reset(self):
        """ Resets the current progress to the start point """
        self.progress = float(self.start)

    def show_progress(self):
        """ Update the progress bar """
        # running in a real terminal
        if hasattr(self.stdout, 'isatty') and self.stdout.isatty():
            self.stdout.write('\r')
        # being piped or redirected
        else:
            self.stdout.write('\n')
        self.stdout.write(str(self))
        self.stdout.flush()


class Ftp:
    """ This class manage a FTP connection, and may also unzip the downloaded file """

    def __init__(self, host, username="anonymous", password="anonymous@", show_progress=False, debug_mode=False,
                 progress=None):
        """ Initialize the FTP Connector

        Args:
            host:               host to connect
            username:           username to use for the connection
            password:           password to use for the connection
            show_progress:      True to visualize the downloading progress
            debug_mode:         True to visualize additional debug information
        """
        if debug_mode:
            self.debug_level = 2
        else:
            self.debug_level = 0
        self.host = host
        self.username = username
        self.password = password
        self.show_progress = show_progress
        self.chunk_count = None
        self.filesize = None
        self.file_count = None
        self.file_nr = None
        self.progress = progress

        self.conn = None
        self._connect()  # sets self.conn

    def _connect(self):
        """ Perform the connection using the passed initialization settings """
        try:
            self.conn = ftplib.FTP(self.host, self.username, self.password)

            self.conn.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.conn.set_debuglevel(self.debug_level)
            self.conn.set_pasv(True)

        except ftplib.error_perm as e:
            log.error("FTP error while connecting to %s: %s" % (self.host, e))
            return
        except socket.error as e:
            log.error("FTP error while connecting to %s: %s" % (self.host, e))
            return

    def disconnect(self):
        """ Close the connection """
        if self.conn:
            self.conn.quit()

    def get_file(self, file_src, file_dst, unzip_it=False):
        """ Retrieve a file

        Args:
            file_src:           File source
            file_dst:           File destination
            unzip_it:           Unzip the retrieved file
        """
        file_dst = os.path.abspath(file_dst)
        if os.path.exists(file_dst):
            os.remove(file_dst)
        self.filesize = self.conn.size(file_src)
        if self.show_progress:
            if self.progress:
                self.progress.start(text="Downloading", has_abortion=True)
            else:
                progress = ProgressBar(end_state=self.filesize, bar_width=50)

        with open(file_dst, 'wb') as f:
            self.chunk_count = 0

            def callback(chunk):
                f.write(chunk)
                self.chunk_count += len(chunk)
                if self.show_progress:

                    if self.progress:
                        if self.progress.canceled:
                            raise RuntimeError("download stopped by user")
                        pt = int((self.chunk_count / self.filesize) * 100.0)
                        self.progress.update(pt)

                    else:
                        progress.add(len(chunk))
                        progress.show_progress()

            self.conn.retrbinary('RETR %s' % file_src, callback)
            if self.show_progress:
                if self.progress:
                    self.progress.end()

        if unzip_it:
            import zipfile

            try:
                z = zipfile.ZipFile(file_dst, "r")

                unzip_path = os.path.dirname(file_dst)

                log.debug("unzipping %s to %s" % (file_dst, unzip_path))

                name_list = z.namelist()
                progress = None
                self.file_nr = len(name_list)
                if self.show_progress:
                    if self.progress:
                        self.progress.start(text="Unzipping", has_abortion=True)
                    else:
                        progress = ProgressBar(end_state=self.file_nr, bar_width=50)

                self.file_count = 0
                for item in name_list:
                    # print(item)
                    z.extract(item, unzip_path)
                    self.file_count += 1
                    if self.show_progress:
                        if self.progress:
                            if self.progress.canceled:
                                raise RuntimeError("unzip stopped by user")
                            pct = int((self.file_count / self.file_nr) * 100.0)
                            self.progress.update(pct)
                        else:
                            progress.add(1)
                            progress.show_progress()
                z.close()
                os.remove(file_dst)
                if self.show_progress:
                    if self.progress:
                        self.progress.end()

            except:
                raise RuntimeError("unable to unzip the downloaded file: %s" % file_dst)
