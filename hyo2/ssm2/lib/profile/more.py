import logging

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt

logger = logging.getLogger(__name__)


class More:
    def __init__(self) -> None:
        self.default_dt = np.float32
        self.sa: npt.NDArray[np.float32] = np.empty((0, 0), dtype=self.default_dt)

    def init_struct_array(self, num_samples: int, fields: list[str]) -> None:
        """Initialize the structured array using the passed num_samples and the len of 'fields' list

        The 'fields' must have as first field the depth
        """
        if len(fields) == 0:
            logger.debug("No 'more' fields")
            return

        dt = [(fld, self.default_dt) for fld in fields]
        self.sa = np.zeros((num_samples, len(fields)), dtype=dt)

    def resize(self, count: int) -> None:
        """Resize the arrays (if present) to the new given number of elements"""
        if self.sa.size == 0:
            return

        if self.sa.shape[0] == count:
            return

        self.sa = np.resize(self.sa, (count, self.sa.shape[1]))

    def debug_plot(self) -> None:
        """Create a debug plot with the data, optionally with the extra data if available"""
        if self.sa.size == 0:
            logger.info("No 'more' samples to plot")
            return

        nr_fields = self.sa.shape[1] - 1
        nr_figures = (nr_fields // 4) + 1

        logger.info("plotting additional %s fields on %s figures" % (nr_fields, nr_figures))

        count = 0  # 0 is depth
        names = self.sa.dtype.names
        for _ in range(nr_figures):  # figure

            if count >= nr_fields:
                break

            plt.figure(dpi=100)

            for j in range(6):  # subplots for figure

                if count >= nr_fields:
                    break

                if j == 0:
                    plt.subplot(231)
                elif j == 1:
                    plt.subplot(232)
                elif j == 2:
                    plt.subplot(233)
                elif j == 3:
                    plt.subplot(234)
                elif j == 4:
                    plt.subplot(235)
                elif j == 5:
                    plt.subplot(236)

                plt.title("%s" % names[count + 1])
                plt.plot(self.sa[names[count + 1]], self.sa[names[0]])
                plt.gca().invert_yaxis()
                plt.grid(True)
                count += 1

            plt.show(block=False)

    def __repr__(self):
        msg = "  <More>\n"
        msg += "    <shape:(%s,%s)>\n" % self.sa.shape
        if self.sa.size != 0:
            for fn in self.sa.dtype.names:
                msg += "    <%s sz:%s min:%.3f max:%.3f>\n" \
                       % (fn, self.sa[fn].shape[0], self.sa[fn].min(), self.sa[fn].max())
        return msg
