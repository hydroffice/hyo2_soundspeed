import numpy as np

import logging

logger = logging.getLogger(__name__)


class DiffTracedProfiles:

    def __init__(self, old_tp, new_tp):
        # required inputs
        self.old_tp = old_tp
        self.new_tp = new_tp
        # optional inputs (otherwise default values)
        self.variable_allowable_error = 0.005
        self.fixed_allowable_error = 0.3

        # output
        self.new_rays = list()
        self.old_rays = list()
        self.max_tolerances = None

    def calc_diff(self):
        if self.old_tp is None:
            raise RuntimeError("first set the old traced profile")
        if self.new_tp is None:
            raise RuntimeError("first set the new traced profile")

        for ang in range(len(self.new_tp.rays)):
            # logger.info("[angle: %d]" % ang)
            ray_new = self.new_tp.rays[ang]
            ray_old = self.old_tp.rays[ang]

            new_t = list()
            new_x = list()
            new_z = list()

            old_t = list()
            old_x = list()
            old_z = list()

            init_done = False
            init_new_t = None
            init_new_x = None
            init_new_z = None
            init_old_t = None
            init_old_x = None
            init_old_z = None

            # first retrieve common areas for both profiles (and reset the 0 values)
            for idx in range(len(ray_new[0])):

                if ray_new[0][idx] == -1:
                    continue
                if ray_old[0][idx] == -1:
                    continue

                if not init_done:
                    # logger.debug("begin z: %s/%s" % (ray_new[2][idx], ray_old[2][idx]))
                    init_new_t = ray_new[0][idx]
                    init_new_x = ray_new[1][idx]
                    init_new_z = ray_new[2][idx]
                    init_old_t = ray_old[0][idx]
                    init_old_x = ray_old[1][idx]
                    init_old_z = ray_old[2][idx]
                    init_done = True

                new_t.append(ray_new[0][idx] - init_new_t)
                new_x.append(ray_new[1][idx] - init_new_x)
                new_z.append(ray_new[2][idx] - init_new_z)

                old_t.append(ray_old[0][idx] - init_old_t)
                old_x.append(ray_old[1][idx] - init_old_x)
                old_z.append(ray_old[2][idx] - init_old_z)

            # logger.debug("end z: %s/%s" % (new_z[-1], old_z[-1]))

            if (len(new_t) == 0) or (len(old_t) == 0):
                self.new_rays.append(np.array([list(), list(), list()]))
                self.old_rays.append(np.array([list(), list(), list()]))
                return

            new_is_longer = False
            min_time = new_t[-1]
            if new_t[-1] > old_t[-1]:
                min_time = old_t[-1]
                new_is_longer = True
            # logger.debug("new is longer: %s" % new_is_longer)
            # logger.debug("min time: %s" % min_time)

            n_t = list()
            n_x = list()
            n_z = list()

            # stop to the minimum common time
            for idx in range(len(new_t)):
                if new_t[idx] > min_time:
                    break

                n_t.append(new_t[idx])
                n_x.append(new_x[idx])
                n_z.append(new_z[idx])

            o_t = list()
            o_x = list()
            o_z = list()

            # stop to the minimum common time
            for idx in range(len(old_t)):
                if old_t[idx] > min_time:
                    break

                o_t.append(old_t[idx])
                o_x.append(old_x[idx])
                o_z.append(old_z[idx])

            self.new_rays.append(np.array([n_t, n_x, n_z]))
            self.old_rays.append(np.array([o_t, o_x, o_z]))
